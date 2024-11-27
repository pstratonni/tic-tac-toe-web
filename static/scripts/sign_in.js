const URL = "192.168.178.23";
document.getElementById("form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const user = {
    username: event.target[0].value,
    password: event.target[1].value,
  };

  const response = await fetch(`http://${URL}/sign_in`, {
    method: "POST",
    mode: "cors",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(user),
  });
  const data = await response.json();
 if (response.status)
  for (let prop in data) {
    localStorage.setItem(prop, data[prop]);
  }
  window.location.href = `http://${URL}`;
});
