
(function () {
    const key = "clients_list_saved_view";
    const saveBtn = document.getElementById("save-view");
    const loadBtn = document.getElementById("load-view");
    if (!saveBtn || !loadBtn) return;

    saveBtn.addEventListener("click", () => {
        localStorage.setItem(key, window.location.search || "?");
        alert("Saved current filters.");
    });

    loadBtn.addEventListener("click", () => {
        const q = localStorage.getItem(key);
        if (q) window.location.search = q;
        else alert("No saved view yet.");
    });
})();
