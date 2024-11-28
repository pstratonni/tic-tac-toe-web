const URL = "10.30.72.27";

const createUser = async (event) => {
  event.preventDefault();
  if (event.target[1].value === event.target[2].value) {
    const available = await validUsername(event.target[0].value);

    if (available.flag) {
      document.querySelector(".available").classList.remove("hidden");
      setTimeout(
        () => document.querySelector(".available").classList.add("hidden"),
        2000
      );
      return;
    }

    const user = {
      username: event.target[0].value,
      password: event.target[1].value,
    };
    const response = await fetch(`http://${URL}/create`, {
      method: "POST",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(user),
    });
    if (response.status == 201) {
      const data = await response.json();
      for (let prop in data) {
        localStorage.setItem(prop, data[prop]);
      }
      window.location.href = `http://${URL}`;
    }else{
        console.log('bad request');
        
    }
  } else {
    document.querySelector(".confirm").classList.remove("hidden");
    event.target[1].value = event.target[2].value = "";
    setTimeout(
      document.querySelector(".confirm").classList.add("hidden"),
      2000
    );
    return;
  }
};

const validUsername = async (name) => {
  const response = await fetch(`http://${URL}/available`, {
    method: "POST",
    mode: "cors",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username: name }),
  });
  return await response.json();
};

document.getElementById("form_up").addEventListener("submit", createUser);
