type Bar = {
    id: string
}

type Baz = {
    age: string
}

type Result = Bar & Baz


const ids: Result = {id:"dasdas", age:"asdas"}