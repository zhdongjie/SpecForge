const email = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
const phoneNumber = /^1[3-9]\d{9}$/
const password = /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z\d]*$/

export default { email, phoneNumber, password }
