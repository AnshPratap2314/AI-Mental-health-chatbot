const API_URL = String(
    window.MINDCARE_API_URL ||
    (window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000"
        : "https://mindcare-ai-wff8.onrender.com")
).replace(/\/$/, "");

const chatMessages =
    document.getElementById("chatMessages");

const chatForm =
    document.getElementById("chatForm");

const messageInput =
    document.getElementById("messageInput");

const sendButton =
    document.getElementById("sendButton");

const typingIndicator =
    document.getElementById("typingIndicator");

const riskBadge =
    document.getElementById("riskBadge");

const connectionStatus =
    document.getElementById("connectionStatus");

const connectionStatusText =
    document.getElementById("connectionStatusText");

const newChatButton =
    document.getElementById("newChatButton");

let sessionId =
    localStorage.getItem("mindcare_session_id");

let isSending = false;

let userInteracting = false;

async function fetchWithTimeout(
    url,
    options = {},
    timeout = 70000
) {
    const controller =
        new AbortController();

    const timer =
        setTimeout(
            () => controller.abort(),
            timeout
        );

    try {
        return await fetch(
            url,
            {
                ...options,
                signal: controller.signal
            }
        );
    } finally {
        clearTimeout(timer);
    }
}

function isNearBottom() {
    const distance =
        chatMessages.scrollHeight -
        chatMessages.scrollTop -
        chatMessages.clientHeight;

    return distance < 140;
}

function scrollToBottom(
    behavior = "smooth"
) {
    requestAnimationFrame(() => {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior
        });
    });
}

function keepInputVisible() {
    if (!messageInput) {
        return;
    }

    setTimeout(() => {
        messageInput.scrollIntoView({
            block: "nearest",
            behavior: "smooth"
        });
    }, 80);
}

function setConnectionStatus(online, text) {
    if (connectionStatus) {
        connectionStatus.classList.toggle("offline", !online);
    }

    if (connectionStatusText) {
        connectionStatusText.textContent = text;
    }
}

async function checkBackendHealth() {
    setConnectionStatus(false, "Checking connection...");

    try {
        const response = await fetchWithTimeout(
            `${API_URL}/health`,
            { method: "GET" },
            8000
        );

        if (!response.ok) {
            throw new Error(`Health check failed (${response.status})`);
        }

        setConnectionStatus(true, "Online & ready to listen");
        return true;
    } catch (error) {
        console.warn("MindCare health check failed:", error);
        setConnectionStatus(false, "Offline — retrying when you send");
        return false;
    }
}

async function createSession() {
    const response =
        await fetchWithTimeout(
            `${API_URL}/session`,
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify({
                    user_name: "friend"
                })
            }
        );

    if (!response.ok) {
        const error =
            await response
                .json()
                .catch(() => ({}));

        throw new Error(
            error.detail ||
            `Session creation failed (${response.status})`
        );
    }

    const data =
        await response.json();

    if (!data.session_id) {
        throw new Error(
            "Server did not return a session ID."
        );
    }

    sessionId =
        data.session_id;

    setConnectionStatus(true, "Online & ready to listen");

    localStorage.setItem(
        "mindcare_session_id",
        sessionId
    );

    return sessionId;
}

async function ensureSession() {
    if (sessionId) {
        return sessionId;
    }

    return createSession();
}

function addMessage(
    message,
    type
) {
    const shouldScroll =
        isNearBottom();

    const messageElement =
        document.createElement("div");

    messageElement.className =
        `message ${type}`;

    const bubble =
        document.createElement("div");

    bubble.className =
        "bubble";

    bubble.textContent =
        String(message || "");

    messageElement.appendChild(
        bubble
    );

    chatMessages.appendChild(
        messageElement
    );

    if (shouldScroll || type === "user") {
        scrollToBottom(
            "smooth"
        );
    }
}

function removeWelcome() {
    const welcome =
        document.querySelector(".welcome");

    if (welcome) {
        welcome.remove();
    }
}

function setTyping(visible) {
    typingIndicator.classList.toggle(
        "hidden",
        !visible
    );

    if (visible) {
        scrollToBottom(
            "smooth"
        );
    }
}

function updateRiskBadge(
    riskLevel
) {
    const level =
        String(
            riskLevel || "low"
        ).toLowerCase();

    if (level === "high") {
        riskBadge.textContent =
            "Safety support";
    } else if (
        level === "moderate"
    ) {
        riskBadge.textContent =
            "Support needed";
    } else {
        riskBadge.textContent =
            "Safe";
    }

    riskBadge.className =
        `risk-badge risk-${level}`;
}

function showConnectionError(
    error
) {
    console.error(
        "MindCare API error:",
        error
    );

    setConnectionStatus(false, "Offline — please try again");

    addMessage(
        "I couldn't connect to MindCare right now. The service may be waking up. Please wait a few seconds and try again.",
        "bot"
    );
}

async function sendMessage(
    message
) {
    const cleanMessage =
        String(
            message || ""
        ).trim();

    if (
        !cleanMessage ||
        isSending
    ) {
        return;
    }

    isSending = true;

    sendButton.disabled =
        true;

    sendButton.classList.add(
        "sending"
    );

    removeWelcome();

    addMessage(
        cleanMessage,
        "user"
    );

    messageInput.value =
        "";

    resizeTextarea();

    setTyping(true);

    try {
        await ensureSession();

        let response =
            await fetchWithTimeout(
                `${API_URL}/chat`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json"
                    },
                    body: JSON.stringify({
                        session_id:
                            sessionId,
                        message:
                            cleanMessage
                    })
                },
                70000
            );

        if (response.status === 404) {
            localStorage.removeItem(
                "mindcare_session_id"
            );

            sessionId = null;

            await createSession();

            response =
                await fetchWithTimeout(
                    `${API_URL}/chat`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type":
                                "application/json"
                        },
                        body: JSON.stringify({
                            session_id:
                                sessionId,
                            message:
                                cleanMessage
                        })
                    },
                    70000
                );
        }

        if (!response.ok) {
            const errorData =
                await response
                    .json()
                    .catch(() => ({}));

            throw new Error(
                errorData.detail ||
                `Chat request failed (${response.status})`
            );
        }

        const data =
            await response.json();

        setConnectionStatus(true, "Online & ready to listen");
        setTyping(false);

        updateRiskBadge(
            data.risk_level
        );

        addMessage(
            data.reply ||
            "I'm here to listen. Tell me more about what's happening.",
            "bot"
        );

    } catch (error) {
        setTyping(false);

        showConnectionError(
            error
        );

    } finally {
        isSending = false;

        sendButton.disabled =
            false;

        sendButton.classList.remove(
            "sending"
        );

        requestAnimationFrame(() => {
            messageInput.focus({
                preventScroll: true
            });
        });
    }
}

function resizeTextarea() {
    messageInput.style.height =
        "auto";

    messageInput.style.height =
        `${Math.min(
            messageInput.scrollHeight,
            140
        )}px`;
}

chatForm.addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        await sendMessage(
            messageInput.value
        );
    }
);

messageInput.addEventListener(
    "keydown",
    async event => {
        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();

            await sendMessage(
                messageInput.value
            );
        }
    }
);

messageInput.addEventListener(
    "input",
    () => {
        resizeTextarea();

        if (
            window.innerWidth <= 800
        ) {
            keepInputVisible();
        }
    }
);

chatMessages.addEventListener(
    "scroll",
    () => {
        userInteracting = true;

        clearTimeout(
            chatMessages._scrollTimer
        );

        chatMessages._scrollTimer =
            setTimeout(() => {
                userInteracting = false;
            }, 120);
    },
    {
        passive: true
    }
);

function attachSuggestionHandlers() {
    document
        .querySelectorAll(".suggestion")
        .forEach(button => {
            button.onclick = () => {
                const message =
                    button.dataset.message;

                sendMessage(
                    message
                );
            };
        });
}

function resetChatUI() {
    chatMessages.innerHTML = `
        <div class="welcome">
            <div class="welcome-icon">
                ✦
            </div>

            <div class="welcome-eyebrow">
                A private space to talk
            </div>

            <h2>What's on your mind?</h2>

            <p>
                You can talk openly about how you're feeling.
                I'm here to listen.
            </p>

            <div class="suggestions">

                <button
                    class="suggestion"
                    data-message="I feel lonely"
                    type="button"
                >
                    <span>💭</span>
                    I feel lonely
                </button>

                <button
                    class="suggestion"
                    data-message="I'm having a difficult day"
                    type="button"
                >
                    <span>🌧</span>
                    I'm having a difficult day
                </button>

                <button
                    class="suggestion"
                    data-message="I just want to talk"
                    type="button"
                >
                    <span>💬</span>
                    I just want to talk
                </button>

                <button
                    class="suggestion"
                    data-message="I'm feeling anxious"
                    type="button"
                >
                    <span>🌿</span>
                    I'm feeling anxious
                </button>

            </div>
        </div>
    `;

    riskBadge.textContent =
        "Safe";

    riskBadge.className =
        "risk-badge risk-low";

    attachSuggestionHandlers();

    scrollToBottom(
        "instant"
    );
}

newChatButton.addEventListener(
    "click",
    async () => {
        if (isSending) {
            return;
        }

        const oldSessionId = sessionId;

        if (oldSessionId) {
            try {
                await fetchWithTimeout(
                    `${API_URL}/session/${encodeURIComponent(oldSessionId)}`,
                    { method: "DELETE" },
                    8000
                );
            } catch (error) {
                console.warn("Could not delete previous session:", error);
            }
        }

        localStorage.removeItem(
            "mindcare_session_id"
        );

        sessionId = null;

        resetChatUI();

        try {
            await ensureSession();
        } catch (error) {
            console.error(
                "Session creation failed:",
                error
            );
        }

        messageInput.focus({
            preventScroll: true
        });
    }
);

function handleViewportResize() {
    document.documentElement.style.setProperty(
        "--viewport-height",
        `${window.visualViewport
            ? window.visualViewport.height
            : window.innerHeight}px`
    );

    if (
        window.innerWidth <= 800 &&
        document.activeElement === messageInput
    ) {
        keepInputVisible();
    }
}

window.addEventListener(
    "resize",
    handleViewportResize,
    {
        passive: true
    }
);

if (window.visualViewport) {
    window.visualViewport.addEventListener(
        "resize",
        handleViewportResize,
        {
            passive: true
        }
    );

    window.visualViewport.addEventListener(
        "scroll",
        handleViewportResize,
        {
            passive: true
        }
    );
}

window.addEventListener(
    "load",
    async () => {
        handleViewportResize();

        console.log(
            "MindCare API:",
            API_URL
        );

        try {
            await ensureSession();

            console.log("MindCare session ready.");
        } catch (error) {
            console.error(
                "Session initialization failed:",
                error
            );
        }

        attachSuggestionHandlers();
        await checkBackendHealth();

        setTimeout(() => {
            messageInput.focus({
                preventScroll: true
            });
        }, 300);
    }
);

window.addEventListener(
    "pageshow",
    () => {
        handleViewportResize();
    }
);

document.addEventListener(
    "visibilitychange",
    () => {
        if (
            document.visibilityState ===
            "visible"
        ) {
            handleViewportResize();
        }
    }
);