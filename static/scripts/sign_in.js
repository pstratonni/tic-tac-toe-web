const URL = '10.30.72.27'
document.getElementById('form').addEventListener('submit', (event) =>  {
    event.preventDefault()
    const data = {
        name: event.target[0].value,
        pass: event.target[1].value
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