type UserProps = {
    name: string;
    age: number
}

type Admin = UserProps & {
    hasPermission: boolean
}

function isAdmin(values: Admin) : Admin {
    return values
}

const admin1 = isAdmin({name:"juswa", age:12, hasPermission:true})