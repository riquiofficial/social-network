document.addEventListener("DOMContentLoaded", function () {
  const like = document.querySelectorAll(".btn-like");
  const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;
  //add likePost function to on click event for every like button
  like.forEach((btn) => {
    btn.addEventListener("click", (event) => {
      event.preventDefault();
      likePost(btn, csrf);
    });
  });
});

// sent PUT request sending id of post and change depending
// on if class has like or unlike rendered
function likePost(likedBtn, csrf) {
  const id = likedBtn.id;
  let liked = likedBtn.classList;

  // include csrf token in request to url for security
  fetch(`/like/${id}`, {
    method: "PUT",
    headers: {
      "X-CSRFToken": csrf,
      "Content-Type": "application/json",
    },
    mode: "same-origin",
    body: JSON.stringify({
      id: id,
      liked: true,
    }),
  })
    .then(() => changeStyle())
    .catch((error) => console.warn("failed", error));

  // Check if liked or unliked by using classes and switch style
  const changeStyle = () => {
    //update 'likes' count using class with correct id
    let likeCount = document.querySelector(`.like${id}`);

    if (liked.contains("btn-primary")) {
      likeCount.innerHTML = `${parseInt(likeCount.innerHTML[0]) + 1} Likes`;
      liked.remove("btn-primary");
      liked.add("btn-secondary");
      likedBtn.innerText = "Unlike";
    } else {
      likeCount.innerHTML = `${parseInt(likeCount.innerHTML[0]) - 1} Likes`;
      liked.remove("btn-secondary");
      liked.add("btn-primary");
      likedBtn.innerText = "Like";
    }
  };
}
