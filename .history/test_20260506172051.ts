type User = {
    id: number
    name: string
    age: number
}


let users: User[] = [
    {id: 1, name: "juswa", age:12},
    {id:2, name:"mark", age: 1}
]



export function updateUser(id: number, data: Partial<User>){
    const newUpdatedUsers = users.map((user) =>{
        if(user.id === id){     
            return{
                ...user,
                ...data
            }
        }
    })  
    return newUpdatedUsers
}


const updateUserOne = updateUser(1, {name:"markiebou"})
console.log(updateUserOne)