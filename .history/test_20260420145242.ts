type Users = {
    name: string;
    age: number;
};

const addUsers = (userInfo:Users) : Users =>{
    return userInfo
}


const user1 = addUsers({name:"juswa", age:12})
console.log(user1)
