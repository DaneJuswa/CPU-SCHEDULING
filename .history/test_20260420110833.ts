type Shoes = {
    brand: string;
    price: number;
}

type otherInfo = {
    size: string;
    type: string
}


type FullShoes = Shoes & otherInfo;

const getShoes = (shoe: Shoes, others: otherInfo = { size:"12", type:"rubber shoes"}) : FullShoes | Shoes => {
    return others ? {...shoe, ...others} : shoe
}


const shoe1 = getShoes({brand: "PUMA", price: 4000});
const shoe2 = getShoes({brand: "Kobne", price:2500}, {size:"12", type:"rubber shoes"})
console.log(shoe1)
console.log(shoe2)