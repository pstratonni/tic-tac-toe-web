const URL = '10.30.72.27'

const  createUser = async (event) => {
    event.preventDefault()
    const available = await validUsername(event.target[0].value)
    if (!available) {
        document.querySelector('.available').classList. remove('hidden')
        setTimeout(document.querySelector('.available').classList. add('hidden'),2000)
        return
    }
    
}

const validUsername = async (name) => {
    const response = await fetch(`http://${URL}/sign_up`,{
        method: "POST",
        mode:"cors",
        credentials: "include",
        headers : {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({name})
    })
    return await response.json()
}


document.getElementById('form').addEventListener('submit', createUser)