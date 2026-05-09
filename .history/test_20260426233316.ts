type finalOutput = Set<string>
const listOfnames: string[] = ["john", "mark", "john"]

function dupples(lits: string[]): finalOutput {

    const transferToSet = new Set(lits)

    return(transferToSet)
}


const news = dupples(listOfnames)
console.log(news)