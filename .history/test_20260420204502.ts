type user = {
    name?: string
    email: string;
    password: string
}

type Admin = user  & {
    hasPermission: boolean
}


let person: user | Admin;

function isAdmin(person: user | Admin): person is Admin{
    return (person as Admin).hasPermission === true
}


const user1: Admin = {email: "user1 ", password:"sadas", hasPermission:true }
const user2: user = {email: "user2", password:"sadas"}

console.log(user1)
console.log(user2)