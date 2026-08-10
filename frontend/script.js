const API_URL =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000"
        : "https://mindcare-ai-wff8.onrender.com";


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

const newChatButton =
    document.getElementById("newChatButton");


let sessionId =
    localStorage.getItem(
        "mindcare_session_id"
    );

let isSending = false;


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
                signal:
                    controller.signal
            }
        );
    } finally {
        clearTimeout(timer);
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

    return await createSession();
}


function addMessage(
    message,
    type
) {
    const messageElement =
        document.createElement("div");

    messageElement.className =
        `message ${type}`;

    const bubble =
        document.createElement("div");

    bubble.className =
        "bubble";

    bubble.textContent =
        message;

    messageElement.appendChild(
        bubble
    );

    chatMessages.appendChild(
        messageElement
    );

    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


function removeWelcome() {
    const welcome =
        document.querySelector(
            ".welcome"
        );

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
        chatMessages.scrollTop =
            chatMessages.scrollHeight;
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

    removeWelcome();

    addMessage(
        cleanMessage,
        "user"
    );

    messageInput.value =
        "";

    messageInput.style.height =
        "auto";

    setTyping(true);

    try {
        await ensureSession();

        const response =
            await fetchWithTimeout(
                `${API_URL}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            session_id:
                                sessionId,
                            message:
                                cleanMessage
                        })
                },
                70000
            );

        if (!response.ok) {
            const errorData =
                await response
                    .json()
                    .catch(() => ({}));

            if (
                response.status === 404
            ) {
                localStorage.removeItem(
                    "mindcare_session_id"
                );

                sessionId = null;

                await createSession();

                const retryResponse =
                    await fetchWithTimeout(
                        `${API_URL}/chat`,
                        {
                            method:
                                "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({
                                    session_id:
                                        sessionId,
                                    message:
                                        cleanMessage
                                })
                        },
                        70000
                    );

                if (!retryResponse.ok) {
                    throw new Error(
                        "Unable to send message after creating a new session."
                    );
                }

                const retryData =
                    await retryResponse.json();

                setTyping(false);

                updateRiskBadge(
                    retryData.risk_level
                );

                addMessage(
                    retryData.reply,
                    "bot"
                );

                return;
            }

            throw new Error(
                errorData.detail ||
                `Chat request failed (${response.status})`
            );
        }

        const data =
            await response.json();

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

        messageInput.focus();
    }
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
        messageInput.style.height =
            "auto";

        messageInput.style.height =
            `${Math.min(
                messageInput.scrollHeight,
                130
            )}px`;
    }
);


function attachSuggestionHandlers() {
    document
        .querySelectorAll(
            ".suggestion"
        )
        .forEach(button => {
            button.onclick =
                () => {
                    const message =
                        button.dataset
                            .message;

                    sendMessage(
                        message
                    );
                };
        });
}


newChatButton.addEventListener(
    "click",
    async () => {
        if (isSending) {
            return;
        }

        localStorage.removeItem(
            "mindcare_session_id"
        );

        sessionId = null;

        chatMessages.innerHTML = `
            <div class="welcome">
                <div class="welcome-icon">
                    ✦
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
                    >
                        I feel lonely
                    </button>

                    <button
                        class="suggestion"
                        data-message="I'm having a difficult day"
                    >
                        I'm having a difficult day
                    </button>

                    <button
                        class="suggestion"
                        data-message="I just want to talk"
                    >
                        I just want to talk
                    </button>

                </div>
            </div>
        `;

        riskBadge.textContent =
            "Safe";

        riskBadge.className =
            "risk-badge risk-low";

        attachSuggestionHandlers();

        try {
            await ensureSession();
        } catch (error) {
            console.error(
                "Session creation failed:",
                error
            );
        }

        messageInput.focus();
    }
);


window.addEventListener(
    "load",
    async () => {
        console.log(
            "MindCare API:",
            API_URL
        );

        try {
            await ensureSession();

            console.log(
                "MindCare session ready:",
                sessionId
            );

        } catch (error) {
            console.error(
                "Session initialization failed:",
                error
            );
        }

        attachSuggestionHandlers();

        messageInput.focus();
    }
);