const dupple = <T>(lits: T[]): T[] =>  {
    return [...new Set(lits)]
}

const value2 = dupple([12, "string", 12])
console.log(value2)