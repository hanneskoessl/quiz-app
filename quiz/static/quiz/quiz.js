function copyLink() {
    const input = document.getElementById("shareLink");

    navigator.clipboard.writeText(input.value).then(() => {
        console.log("Copied!");
    });
}