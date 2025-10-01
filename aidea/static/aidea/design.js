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

//選んだ工芸品名をサーバーに送って、AIから返ってきた注意点を画面に表示するボタンの処理
document.addEventListener("DOMContentLoaded", () => { //DOMContentLoadedでHTMLの全ての全要素が読み込まれたタイミングで処理を開始する
    const btn = document.getElementById("generate-btn");  

    // URLから item パラメータを取得
    const urlParams = new URLSearchParams(window.location.search);
    const item = urlParams.get("item") || "工芸品";

    btn.addEventListener("click", async () => {
        try {
            const response = await fetch("/aidea/generate/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"), // ← DjangoのCSRFトークン
                },
                body: JSON.stringify({ item: item }),
            });

            if (!response.ok) {
                throw new Error("サーバーエラー: " + response.status);
            }

            const data = await response.json();
            document.getElementById("result").innerText = data.text || "結果がありません。";
        } catch (error) {
            console.error("エラー:", error);
            document.getElementById("result").innerText = "エラーが発生しました。";
        }
    });
});
