async function fetchData<T>(url: string): Promise<T>{
    const res = await fetch(url)
    const data: T = await res.json()
    return data
}



type User = {
    id: number
    name: string
    age:  number
}


type Product = {
    id: number
    productName: string
    cost: number
}


async function getUsers() {
    const user = await fetchData<User>("api/users")
    console.log()
}

async function getProducst() {
    const products = await fetchData<Product>("api/products")
}