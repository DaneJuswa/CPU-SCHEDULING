type User = {
    name: string;
    password: string;
}

type Admin = User & {
    hasPermission: boolean
}


function isValid(person: User | Admin) : person is Admin{
    return (person as Admin).hasPermission === true
}

function deletePost(user: User | Admin){
    if (isValid(user)){
        console.log("deleted post")
    }else{
        console.log("unauthorized access")
    }
}


const user1: User = {name:"john", password:"123"}