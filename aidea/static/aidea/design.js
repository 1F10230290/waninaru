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
    let messagesForApi = [
        ...messages.slice(0,-1),
        {role: "user", content: promptToSend}
    ];

    const itemName = document.querySelector(".suggest-btn").dataset.itemName || "日本の伝統工芸品";

    try {
        const response = await fetch("/aidea/generate/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({
                 messages: messagesForApi , // AI用の会話履歴を送信
                item_name: itemName}),
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
            
            const buttonText = btn.textContent;
            let finalPrompt = "";

            if (command === "famous_design") {
                //「代表的な模様やモチーフは？」
                finalPrompt = `
                「${itemName}」のデザインのヒントとして、伝統的に使われる代表的な「模様」や「モチーフ」（例：植物、動物、幾何学模様など）を3〜5個教えてください。
                それぞれのモチーフについて、
                - デザインの意味（例：縁起が良い、など）
                - デザインに取り入れる際の簡単なヒントを簡潔に説明してください。
                - あなたが持つべき役割や制約条件は、システムプロンプトの指示に厳密に従ってください。
                `;
            } 
            
            else if (command === "easy_design") {
                //「初心者向けの簡単なデザイン案は？」
                finalPrompt = `
                私はデザイン初心者です。「${itemName}」の特性を活かしつつ、初心者でも描きやすい「シンプルなデザイン案」を2つ提案してください。
                - なぜそれが描きやすいのか（例：複雑な曲線が少ない、使う色が少ない）
                - 簡単なデザインの構成を教えてください。
                - あなたが持つべき役割や制約条件は、システムプロンプトの指示に厳密に従ってください。
                `;
            } 

            else if (command === "drawing_tips") {
                //「描き方のコツは？」 (既存のプロンプト)
                finalPrompt = `# 指示
                私はアマチュアクリエイターです。「${itemName}」の表面に描くためのデザイン案を、立体的なイラストとして描きたいです。
                既に、${itemName}を模った枠線は用意してあり、塗り絵の状態です。
                プロのデザイナーが初心者に教えるように、専門用語を使わずにステップバイステップ形式でアドバイスしてください。

                # 守ってほしい手順
                - **ステップ1**では、まず
                - その後、構図の取り方や、曲面に模様をうまく乗せるコツなどを重点的に教えてください。また、${itemName}で可能な表現についても教えて下さい。
                - あなたが持つべき役割や制約条件は、システムプロンプトの指示に厳密に従ってください。
                `;
            } 
            
            else if (command === "avoid_design") {
                //「デザインで避けるべきことは？」
                finalPrompt = `
                私は「${itemName}」の製造方法を知りません。
                初心者がやりがちだけど、実際の製造（${itemName}）を考えると「技術的に難しい」または「避けるべき」デザインのNG例を教えてください。
                - （例：細すぎる線、特定の部分への彫刻、色の多用など）
                理由とセットで、リスト形式で簡潔に教えてください。
                - あなたが持つべき役割や制約条件は、システムプロンプトの指示に厳密に従ってください。
                `;
            }

            if (finalPrompt) {
                sendMessage(buttonText, finalPrompt);
            }
        });
    });

    const feedbackImageUpload = document.getElementById("feedback-image-upload");
    const getFeedbackBtn = document.getElementById("get-feedback-btn");
    const feedbackResult = document.getElementById("feedback-result");
    const feedbackLoading = document.getElementById("feedback-loading");

    let feedbackUsed = false;

    getFeedbackBtn.addEventListener("click", async () => {
        if(feedbackUsed){
            alert("フィードバックは1回のみ行えます。");
            return;
        }

        console.log("フィードバックボタンがクリックされました！");
        const file = feedbackImageUpload.files[0];
        if (!file) {
            alert("フィードバックを受けたいデザイン画像をアップロードしてください。");
            return;
        }

        feedbackUsed = true;
        
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
            feedbackLoading.style.display = 'none';
            getFeedbackBtn.disabled = true;
        }
    });
});


