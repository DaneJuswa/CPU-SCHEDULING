"use strict";
function addNumbers(valueToAdd, age) {
    if (age) {
        return valueToAdd + 1 + age;
    }
    return valueToAdd + 1;
}
console.log(addNumbers(12));
console.log(addNumbers(14, 6));
