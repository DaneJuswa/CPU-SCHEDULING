type User = { 
    name: string
    age: number
}


export function addUser<T extends {name: string}>(user: T){
    console.log(user.name)
}



const user1 = addUser({name:"john"})
console.log(user1)