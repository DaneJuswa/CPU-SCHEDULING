type Person = {
    name: string,
    age: number     
}


type Woman =  Person & {
    characteristiccs: string,
    familyMembers: string[]
}


const setWomen1 = (Buyer: Person | Woman): Buyer is Woman => {
    return "characteristicccs" in Buyer && "familyMembers" in Buyer
}


const person1 = setWomen1({name: "john", age:12})
console.log(person1)