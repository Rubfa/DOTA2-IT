(function () {
  function bindCounter(scope) {
    var textarea = scope.querySelector("textarea");
    var counter = scope.querySelector("[data-mb-counter]");

    if (!textarea || !counter || textarea.dataset.mbCounterBound === "1") {
      return;
    }

    textarea.dataset.mbCounterBound = "1";

    var max = parseInt(textarea.getAttribute("maxlength") || "0", 10);

    function update() {
      var len = textarea.value.length;
      counter.textContent = max > 0 ? len + "/" + max : String(len);
    }

    textarea.addEventListener("input", update);
    update();
  }

  function toggleReplyBox(id, shouldShow) {
    var box = document.getElementById("reply-box-" + id);
    if (!box) return;

    box.classList.toggle("is-hidden", !shouldShow);

    if (shouldShow) {
      var form = box.querySelector("form");
      if (form) {
        bindCounter(form);
        var textarea = form.querySelector("textarea");
        if (textarea) textarea.focus();
      }
    }
  }

  function init(scope) {
    var root = scope || document;

    root.querySelectorAll("form.post-form, form.reply-form").forEach(function (form) {
      bindCounter(form);
    });
  }

  async function submitHomePanelForm(form) {
    var container = form.closest("[data-home-messageboard='1']");
    var submitButton = form.querySelector("button[type='submit']");
    var currentScroll = window.scrollY;

    if (!container) {
      return false;
    }

    if (form.classList.contains("inline-form") && !window.confirm("Delete this message?")) {
      return true;
    }

    if (submitButton) {
      submitButton.disabled = true;
    }
    container.classList.add("is-busy");

    try {
      var response = await fetch(form.action, {
        method: "POST",
        headers: {
          "X-Requested-With": "XMLHttpRequest"
        },
        body: new FormData(form)
      });

      if (!response.ok) {
        throw new Error("Unexpected status: " + response.status);
      }

      var payload = await response.json();

      if (!payload.html || !window.homePanelController || typeof window.homePanelController.renderPanelPayload !== "function") {
        throw new Error("Message board payload missing panel HTML.");
      }

      window.homePanelController.renderPanelPayload(payload, {
        pushHistory: false,
        scrollY: currentScroll
      });
      return true;
    } catch (error) {
      console.error("Message board request failed.", error);
      return false;
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
      }
      container.classList.remove("is-busy");
    }
  }

  window.initMessageboardUI = init;
  init(document);

  document.addEventListener("click", function (event) {
    var reply = event.target.closest(".reply-link");
    if (reply) {
      event.preventDefault();
      toggleReplyBox(reply.getAttribute("data-reply-to"), true);
      return;
    }

    var cancel = event.target.closest(".cancel-reply");
    if (cancel) {
      event.preventDefault();
      toggleReplyBox(cancel.getAttribute("data-cancel"), false);
    }
  });

  document.addEventListener("submit", function (event) {
    var form = event.target;
    var isMessageForm =
      form.matches("form.post-form") ||
      form.matches("form.reply-form") ||
      form.matches("form.inline-form");

    if (!isMessageForm) {
      return;
    }

    if (!form.closest("[data-home-messageboard='1']")) {
      return;
    }

    event.preventDefault();
    submitHomePanelForm(form);
  });
})();
