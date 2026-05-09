type vechicle = {
    brand: string
    type: string
}


const vechicleOne = {
    brand: "mitsubishi",
    type: "sedan",
    cost: "200"
}


export function printCar(car: vechicle){
    console.log(car)
}



printCar(vechicleOne)