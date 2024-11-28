
document.getElementById("form_in").addEventListener("submit", async (event) => {
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
 if (response.status == 200){
  for (let prop in data) {
    localStorage.setItem(prop, data[prop]);
  }
  window.location.href = `http://${URL}`;
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

document.addEventListener('DOMContentLoaded', (event) => {
  if (window.location.pathname === '/sign_in'){
    document.getElementById('chk').click()
    
  }
  
})
