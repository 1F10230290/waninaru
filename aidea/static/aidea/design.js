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
async function sendMessage(userInput, rawPrompt = null) {
    if (!userInput.trim()) return;

    // ユーザーの発言として画面に表示する内容
    const displayInput = userInput;
    // AIに実際に送る内容（rawPromptがあればそちらを優先）
    const promptToSend = rawPrompt || userInput;

    // ユーザーの発言を履歴に追加（表示用）
    messages.push({ role: "user", content: displayInput });
    renderChat();

    // AIに送るための会話履歴を一時的に作成
    let messagesForApi = [...messages];
    // 最後のメッセージを、AIに送る用のプロンプトで上書き
    messagesForApi[messagesForApi.length - 1].content = promptToSend;

    try {
        const response = await fetch("/aidea/generate/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ messages: messagesForApi }), // AI用の会話履歴を送信
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
                // AIに送る詳細なプロンプト
                finalPrompt = `# 指示
                私はアマチュアクリエイターです。「${itemName}」の表面に描くためのデザイン案を、立体的なイラストとして描きたいです。
                その描き方の手順を、プロのデザイナーが初心者に教えるように、専門用語を使わずにステップバイステップ形式でアドバイスしてください。
                
                # 守ってほしい手順
                - **ステップ1**では、まず「${itemName}」そのものの形を立体図として描く方法を説明してください。例えば、お椀ならその丸みや高台の描き方、お皿ならその深さや縁の表現方法などです。
                - その後、構図の取り方や、曲面に模様をうまく乗せるコツなどを重点的に教えてください。また、${itemName}で可能な表現についても教えて下さい。
                - あなたが持つべき役割や制約条件は、システムプロンプトの指示に厳密に従ってください。
                `;
            }

            if (finalPrompt) {
                // ▼▼▼ この呼び出し方を変更 ▼▼▼
                // 修正前: sendMessage(finalPrompt);
                
                // 修正後:
                // 第1引数に「画面に表示するテキスト」、第2引数に「AIに送るプロンプト」を渡す
                const buttonText = "描き方のコツを教えて"; // "描き方のコツを聞く"
                sendMessage(buttonText, finalPrompt);
            }
        });
    });

const feedbackImageUpload = document.getElementById("feedback-image-upload");
    const getFeedbackBtn = document.getElementById("get-feedback-btn");
    const feedbackResult = document.getElementById("feedback-result");
    const feedbackLoading = document.getElementById("feedback-loading");

    getFeedbackBtn.addEventListener("click", async () => {
        console.log("フィードバックボタンがクリックされました！");
        const file = feedbackImageUpload.files[0];
        if (!file) {
            alert("フィードバックを受けたいデザイン画像をアップロードしてください。");
            return;
        }
        
        // 工芸品名を data-item-name 属性から取得
        const itemName = document.querySelector(".suggest-btn").dataset.itemName || "日本の伝統工芸品";

        const formData = new FormData();
        formData.append("design_image", file);
        formData.append("item_name", itemName); // 工芸品名をサーバーに送信

        // UIを「分析中」の状態に変更
        getFeedbackBtn.disabled = true;
        feedbackLoading.style.display = 'block';
        feedbackResult.innerHTML = "";

        try {
            const response = await fetch("/aidea/get_feedback/", { // 新しいエンドポイント
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: formData,
            });

            if (!response.ok) {
                throw new Error("サーバーエラーが発生しました。");
            }

            const data = await response.json();
            // marked.js を使ってMarkdownをHTMLに変換して表示
            feedbackResult.innerHTML = marked.parse(data.feedback);

        } catch (error) {
            console.error("フィードバック取得エラー:", error);
            feedbackResult.textContent = "エラーが発生しました。もう一度試してください。";
        } finally {
            // UIを元の状態に戻す
            getFeedbackBtn.disabled = false;
            feedbackLoading.style.display = 'none';
        }
    });
});