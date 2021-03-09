document.addEventListener("DOMContentLoaded", function () {
  const editBtn = document.querySelectorAll(".btn-edit");
  const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;

  editBtn.forEach((btn) => {
    btn.addEventListener("click", (event) => {
      event.preventDefault();
      btn.style.display = "none";
      renderEditPost(btn, csrf);
    });
  });
});

function renderEditPost(btn, csrf) {
  // get id from class list
  const id = btn.classList[4].substring(4);
  const content = document.querySelector(`#card-text${id}`);
  const text = content.innerHTML;
  content.innerHTML = `
    <textarea maxlength="250" id="edit-text${id}">${text}</textarea><br />
    <button class="btn btn-sm btn-primary btn-save${id}">Save</button>
    <button class="btn btn-secondary btn-sm" id="cancel-edit${id}">Cancel</button>
    `;

  // Edit data
  const saveBtn = document.querySelector(`.btn-save${id}`);
  const cancelBtn = document.querySelector(`#cancel-edit${id}`);
  let newContent = document.querySelector(`#edit-text${id}`);

  // Cancel edit
  cancelBtn.addEventListener("click", () => {
    content.innerHTML = text;
    btn.style.display = "inline-block";
  });
  // Save edited data to database
  saveBtn.addEventListener("click", () => {
    sendEditContent(newContent.value, id, csrf, content);
    btn.style.display = "inline-block";
  });
}

function sendEditContent(newContent, id, csrf, content) {
  fetch(`/edit/${id}`, {
    method: "PUT",
    headers: {
      "X-CSRFToken": csrf,
      "Content-Type": "application/json",
    },
    mode: "same-origin",
    body: JSON.stringify({
      id: id,
      new_content: newContent,
    }),
  })
    .then((content) => console.log(content))
    // Update post live
    .then(() => (content.innerHTML = newContent))
    .catch((error) => console.log(error));
}
