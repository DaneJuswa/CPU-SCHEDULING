type User = {
    name: string
    age: number
}


type Admin = {
    name: number
    credentials: string
}

type Final = User & Admin


export function printers(userInput: Final){
    console.log(userInput)
}


printers("adas")