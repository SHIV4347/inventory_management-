-- databsae - model
-- Create Users table
CREATE TABLE Users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(100) NOT NULL UNIQUE,
    mobile_number NVARCHAR(15) NOT NULL,
    address NVARCHAR(255) NOT NULL,
    password NVARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);

-- Create Items table
CREATE TABLE Items (
    item_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    item_name NVARCHAR(100) NOT NULL,
    Inventory NVARCHAR(255) NOT NULL,
    price DECIMAL(18, 2) NOT NULL,
    image_path NVARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

delete from users where user_id=4;

select * from Items
select * from Users






