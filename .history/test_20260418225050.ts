type Shoes = {
    brand: String;
    price: number;
}

const getShoes = (shoe: Shoes) : Shoes => {
    return shoe
}


const shoe1 = getShoes({brand: "PUMA", price: 4000})

console.log(shoe1)