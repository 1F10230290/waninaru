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
            const command = btn.dataset.command;
            const itemName = btn.dataset.itemName;
            
            let finalPrompt = "";

            if (command === "drawing_tips") {
                // ▼▼▼ この「超具体的な指示」をAIに送る ▼▼▼
                finalPrompt = `# 指示
                私はアマチュアクリエイターです。
                「${itemName}」の表面に描くためのデザイン案を、立体的なイラストとして描きたいです。
                その描き方の手順を、プロのデザイナーが初心者に教えるように、専門用語を使わずにステップバイステップ形式でアドバイスしてください。

                # 守ってほしい手順
                - **ステップ1**では、まず「${itemName}」そのものの形を立体図として描く方法を説明してください。例えば、お椀ならその丸みや高台の描き方、お皿ならその深さや縁の表現方法などです。
                - その後、構図の取り方や、曲面に模様をうまく乗せるコツなどを重点的に教えてください。また、${itemName}で可能な表現についても教えて下さい。
                - あなたが持つべき役割や制約条件は、システムプロンプトの指示に厳密に従ってください。
                `;
            }

            if (finalPrompt) {
                sendMessage(finalPrompt);
            }
        });
    });
});