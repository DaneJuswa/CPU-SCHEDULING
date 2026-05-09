type Shoes = {
    brand: String;
    price: number;
}

type otherInfo = {
    size: String;
    type: String
}

const getShoes = (shoe: Shoes, others?: otherInfo) : Shoes => {
    return shoe
}


const shoe1 = getShoes({brand: "PUMA", price: 4000})

console.log(shoe1)