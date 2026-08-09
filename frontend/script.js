const API_URL = window.location.hostname === "127.0.0.1" ||
                window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"
    : "https://mindcare-ai-api.onrender.com";

const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const typingIndicator = document.getElementById("typingIndicator");
const riskBadge = document.getElementById("riskBadge");
const newChatButton = document.getElementById("newChatButton");

let sessionId = localStorage.getItem("mindcare_session_id");
let isSending = false;

function setSession(id) {
    sessionId = id;

    if (id) {
        localStorage.setItem(
            "mindcare_session_id",
            id
        );
    } else {
        localStorage.removeItem(
            "mindcare_session_id"
        );
    }
}

async function createSession() {
    const response = await fetch(
        `${API_URL}/session`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_name: "friend"
            })
        }
    );

    if (!response.ok) {
        throw new Error(
            "Unable to create session."
        );
    }

    const data = await response.json();

    if (!data.session_id) {
        throw new Error(
            "Session ID was not returned."
        );
    }

    setSession(data.session_id);

    return sessionId;
}

async function ensureSession() {
    if (sessionId) {
        return sessionId;
    }

    return createSession();
}

async function apiChat(message) {
    await ensureSession();

    let response = await fetch(
        `${API_URL}/chat`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: sessionId,
                message
            })
        }
    );

    if (response.status === 404) {
        setSession(null);

        await createSession();

        response = await fetch(
            `${API_URL}/chat`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    message
                })
            }
        );
    }

    const data = await response.json()
        .catch(() => ({}));

    if (!response.ok) {
        throw new Error(
            typeof data.detail === "string"
                ? data.detail
                : "Unable to send message."
        );
    }

    return data;
}

function addMessage(
    message,
    type,
    meta = null
) {
    const messageElement =
        document.createElement("div");

    messageElement.className =
        `message ${type}`;

    const bubble =
        document.createElement("div");

    bubble.className = "bubble";

    bubble.textContent =
        message || "";

    messageElement.appendChild(
        bubble
    );

    if (meta) {
        const metaElement =
            document.createElement("div");

        metaElement.className =
            "message-meta";

        metaElement.textContent =
            meta;

        messageElement.appendChild(
            metaElement
        );
    }

    chatMessages.appendChild(
        messageElement
    );

    scrollToBottom();
}

function addSystemMessage(message) {
    const element =
        document.createElement("div");

    element.className =
        "system-message";

    element.textContent =
        message;

    chatMessages.appendChild(
        element
    );

    scrollToBottom();
}

function removeWelcome() {
    const welcome =
        document.querySelector(".welcome");

    if (welcome) {
        welcome.remove();
    }
}

function showTyping() {
    typingIndicator.classList.remove(
        "hidden"
    );

    scrollToBottom();
}

function hideTyping() {
    typingIndicator.classList.add(
        "hidden"
    );
}

function scrollToBottom() {
    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}

function updateRiskBadge(riskLevel) {
    const level =
        riskLevel || "low";

    const labels = {
        low: "Safe",
        moderate: "Support needed",
        high: "Safety support"
    };

    riskBadge.textContent =
        labels[level] || "Safe";

    riskBadge.className =
        `risk-badge risk-${level}`;

    document.body.dataset.risk =
        level;
}

function updateConversationState(data) {
    const analysis =
        data.analysis || {};

    const state =
        analysis.state || {};

    const mood =
        state.current_mood ||
        analysis.mood ||
        "neutral";

    const topic =
        state.last_topic ||
        analysis.topic ||
        "general";

    const risk =
        analysis.risk_level ||
        state.current_risk ||
        data.risk_level ||
        "low";

    document.body.dataset.mood =
        mood;

    document.body.dataset.topic =
        topic;

    document.body.dataset.risk =
        risk;

    updateRiskBadge(
        risk
    );
}

function setSending(state) {
    isSending = state;

    sendButton.disabled =
        state;

    messageInput.disabled =
        state;

    sendButton.classList.toggle(
        "sending",
        state
    );
}

function resizeInput() {
    messageInput.style.height =
        "auto";

    messageInput.style.height =
        `${Math.min(
            messageInput.scrollHeight,
            130
        )}px`;
}

async function sendMessage(message) {
    const cleaned =
        (message || "").trim();

    if (
        !cleaned ||
        isSending
    ) {
        return;
    }

    setSending(true);

    removeWelcome();

    addMessage(
        cleaned,
        "user"
    );

    messageInput.value = "";

    resizeInput();

    showTyping();

    try {
        const data =
            await apiChat(
                cleaned
            );

        hideTyping();

        const reply =
            data.reply ||
            data.response ||
            data.message ||
            "I'm here to listen.";

        addMessage(
            reply,
            "bot"
        );

        updateConversationState(
            data
        );
    } catch (error) {
        hideTyping();

        console.error(
            "Chat error:",
            error
        );

        addMessage(
            "I'm having trouble connecting right now. Please check that the MindCare server is running and try again.",
            "bot"
        );
    } finally {
        setSending(false);

        messageInput.focus();

        scrollToBottom();
    }
}

function attachSuggestionEvents() {
    document
        .querySelectorAll(".suggestion")
        .forEach(button => {
            button.addEventListener(
                "click",
                () => {
                    sendMessage(
                        button.dataset.message
                    );
                }
            );
        });
}

function renderWelcome() {
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
                You can talk openly about your thoughts,
                emotions, stress, worries, or anything
                you would like to share.
            </p>

            <div class="suggestions">
                <button
                    class="suggestion"
                    data-message="I feel lonely"
                >
                    <span>💭</span>
                    I feel lonely
                </button>

                <button
                    class="suggestion"
                    data-message="I'm having a difficult day"
                >
                    <span>🌧</span>
                    I'm having a difficult day
                </button>

                <button
                    class="suggestion"
                    data-message="I just want to talk"
                >
                    <span>💬</span>
                    I just want to talk
                </button>

                <button
                    class="suggestion"
                    data-message="I'm feeling anxious"
                >
                    <span>🌿</span>
                    I'm feeling anxious
                </button>
            </div>
        </div>
    `;

    attachSuggestionEvents();

    updateRiskBadge(
        "low"
    );
}

async function startNewChat() {
    if (isSending) {
        return;
    }

    setSession(null);

    renderWelcome();

    try {
        await createSession();

        addSystemMessage(
            "New private conversation started."
        );
    } catch (error) {
        console.error(
            "New session error:",
            error
        );

        addSystemMessage(
            "Unable to create a new session. Please try again."
        );
    }

    messageInput.focus();
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
    resizeInput
);

newChatButton.addEventListener(
    "click",
    startNewChat
);

window.addEventListener(
    "load",
    async () => {
        attachSuggestionEvents();

        try {
            await ensureSession();
        } catch (error) {
            console.error(
                "Session initialization failed:",
                error
            );
        }

        messageInput.focus();
    }
);