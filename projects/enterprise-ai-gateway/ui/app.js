const elModel = document.getElementById("model");
const elChat = document.getElementById("chat");
const elPrompt = document.getElementById("prompt");
const elSend = document.getElementById("send");

const state = {
  messages: []
};

function addMessage(role, content) {
  state.messages.push({ role, content });
  const div = document.createElement("div");
  div.className = `msg ${role === "user" ? "user" : "ai"}`;
  div.textContent = `${role === "user" ? "You" : "AI"}: ${content}`;
  elChat.appendChild(div);
  elChat.scrollTop = elChat.scrollHeight;
}

async function loadModels() {
  const res = await fetch("/api/models");
  const models = await res.json();
  elModel.innerHTML = "";
  for (const m of models) {
    const opt = document.createElement("option");
    opt.value = m.id;
    opt.textContent = `${m.display_name} (${m.provider})`;
    elModel.appendChild(opt);
  }
}

async function send() {
  const text = (elPrompt.value || "").trim();
  if (!text) return;
  elPrompt.value = "";
  addMessage("user", text);

  elSend.disabled = true;
  try {
    const payload = {
      model_id: elModel.value,
      messages: state.messages
    };
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) {
      addMessage("assistant", `Error: ${data.detail || "request failed"}`);
      return;
    }
    addMessage("assistant", data.content || "");
  } finally {
    elSend.disabled = false;
  }
}

elSend.addEventListener("click", send);
elPrompt.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
    send();
  }
});

loadModels().catch(() => {
  addMessage("assistant", "Failed to load models. Check API connectivity.");
});
