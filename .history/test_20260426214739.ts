type User = {
    name: string;
    age: number
}

type Admin = User & {
    isAdmin:boolean;
    password: string
}


function checkIsAdmin( person : (User | Admin)) : person is Admin {
    if ((person as Admin).isAdmin === true){
        console.log("post deleted")
        return true
    }else{
        console.log("u dont have access")
        return false
    }
}


const personOne = checkIsAdmin({name: "joshua", age: 12, isAdmin:true})
const personTwo = checkIsAdmin({name: "joshua", age: 12})
