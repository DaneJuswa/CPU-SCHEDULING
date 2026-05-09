type User = {
    name:string;
    password: string
}

type Admin = User & {
    hasPermission: boolean;
}

function isAdmin(person: User | Admin): person is Admin{
    return (person as Admin).hasPermission === true    
}

function deletePost(user: User | Admin){
    if (isAdmin(user)){
        console.log("post deleted")
    }else{
        console.log("u dont have access")
    }

}


const user1: Admin = {name:"admin1", password: "password123", hasPermission:true}
const user2: User = {name:"admin1", password: "password123"}


deletePost(user1)
deletePost(user2)