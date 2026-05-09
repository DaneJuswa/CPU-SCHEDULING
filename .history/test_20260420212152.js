"use strict";
function isValid(person) {
    return person.hasPermission === true;
}
function deletePost(user) {
    if (isValid(user)) {
        console.log("deleted post");
    }
    else {
        console.log("unauthorized access");
    }
}
const user1 = { name: "john", password: "123" };
const user2 = { name: "john", password: "123", hasPermission: true };


deletePost(user1)
deletePost(user2)