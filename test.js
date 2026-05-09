export function addUser(user) {
    console.log(user.name);
}
const user1 = addUser({ name: "john" });
console.log(user1);
