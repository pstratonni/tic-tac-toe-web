const URL = '192.168.178.23'
document.getElementById('form').addEventListener('submit', (event) =>  {
    event.preventDefault()
    const data = {
        username: event.target[0].value,
        password: event.target[1].value
    }
    try{
        fetch(`http://${URL}/sign_in`,{
            method: "POST",
            mode:"cors",
            credentials: "include",
            headers : {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data)
        }).then((response) => {
            return response.json()
        }).then((data) => {
                console.log(data)
        })
    }
    catch{}
    
    
})