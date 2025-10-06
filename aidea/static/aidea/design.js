// =========================
// CSRFトークン取得用関数
// =========================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // name= の形を探す
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//会話履歴
let messages=[];  //ユーザーとAIのメッセージ履歴

function renderChat() {
    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML = "";

    messages.forEach(msg => {
        const div = document.createElement("div");
        div.className = msg.role === "user" ? "user-message" : "assistant-message";
        div.innerHTML = marked.parse(msg.content);
        chatBox.appendChild(div);
    });

    chatBox.scrollTop = chatBox.scrollHeight; // 自動スクロール
}

//メッセージの送信
async function sendMessage(userInput) {
    if (!userInput.trim()) return;

    // ユーザーの発言を履歴に追加
    messages.push({ role: "user", content: userInput });
    renderChat();

    try {
        const response = await fetch("/aidea/generate/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ messages: messages }),
        });

        if (!response.ok) throw new Error("サーバーエラー: " + response.status);

        const data = await response.json();

        // AIの返答を履歴に追加
        messages.push({ role: "assistant", content: data.text });
        renderChat();
    } catch (error) {
        console.error("エラー:", error);
        messages.push({ role: "assistant", content: "エラーが発生しました。" });
        renderChat();
    }

    // 入力欄をクリア
    document.getElementById("free-input").value = "";
}


//選んだ工芸品名をサーバーに送って、AIから返ってきた注意点を画面に表示するボタンの処理
document.addEventListener("DOMContentLoaded", () => {
    const freeBtn = document.getElementById("free-btn");
    const freeInput = document.getElementById("free-input");

    freeBtn.addEventListener("click", () => sendMessage(freeInput.value));

    freeInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage(freeInput.value);
    });

    // 推奨質問ボタンの処理
    const suggestBtns = document.querySelectorAll(".suggest-btn");
    suggestBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const question = btn.dataset.question; // data-question属性の内容
            sendMessage(question);
        });
    });
});