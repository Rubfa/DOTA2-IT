(function () {
  console.log("[messageboard] message.js loaded");

  function bindCounter(scope) {
    var textarea = scope.querySelector("textarea");
    var counter = scope.querySelector("[data-mb-counter]");
    if (!textarea || !counter) return;

    var max = parseInt(textarea.getAttribute("maxlength") || "0", 10);

    function update() {
      var len = textarea.value.length;
      counter.textContent = max > 0 ? len + "/" + max : String(len);
    }

    textarea.addEventListener("input", update);
    update();
  }

  document.querySelectorAll("form.post-form, form.reply-form").forEach(function (f) {
    bindCounter(f);
  });

  document.addEventListener("click", function (e) {
    var reply = e.target.closest(".reply-link");
    if (reply) {
      e.preventDefault();
      var id = reply.getAttribute("data-reply-to");
      var box = document.getElementById("reply-box-" + id);
      if (box) {
        box.style.display = "block";
        var form = box.querySelector("form");
        if (form) {
          bindCounter(form);
          var t = form.querySelector("textarea");
          if (t) t.focus();
        }
      }
      return;
    }

    var cancel = e.target.closest(".cancel-reply");
    if (cancel) {
      e.preventDefault();
      var id2 = cancel.getAttribute("data-cancel");
      var box2 = document.getElementById("reply-box-" + id2);
      if (box2) box2.style.display = "none";
      return;
    }
  });
})();