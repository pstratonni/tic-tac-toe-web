document.getElementById("form_in").addEventListener("submit", async (event) => {
  event.preventDefault();
  const user = {
    username: event.target[0].value,
    password: event.target[1].value,
  };

  const response = await fetch(`${URL}/sign_in`, {
    method: "POST",
    mode: "cors",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(user),
  });
  const data = await response.json();
 if (response.status == 200){
  for (let prop in data) {
    localStorage.setItem(prop, data[prop]);
  }
  document.getElementById("modal").classList.add("hidden");
  await ready()
  addName()
  }else{
    document.querySelector(".not-exist").classList.remove("hidden");
    event.target[0].value = event.target[1].value = "";
    setTimeout(
      document.querySelector(".not-exist").classList.add("hidden"),
      2000
    );
    return;
  }
});
