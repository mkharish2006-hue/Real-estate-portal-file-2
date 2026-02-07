# Business Architecture, Conceptual and Logical Models for Real Estate Portal

## Business Architecture Diagram

The business architecture outlines the key business capabilities, processes, and entities for the real estate portal.

### Key Entities:
- **User**: Buyers and sellers who register and interact on the platform.
- **Property**: Land/houses listed for sale by sellers.
- **Review**: Feedback from buyers on sellers after transactions.
- **Transaction**: Purchase process (simplified as status on property).

### Business Processes:
1. **User Registration**: Users create accounts.
2. **Property Listing**: Sellers add properties.
3. **Property Browsing**: Buyers search and view properties.
4. **Contact/Inquiry**: Buyers contact sellers.
5. **Purchase**: Buyer marks property as purchased.
6. **Review Submission**: Buyers review sellers.
7. **Profile Management**: Users edit profiles.

### Text-Based Diagram (High-Level Flow):

```
[User Registration] --> [Login] --> [Dashboard]
                              |
                              v
[Property Listing] <-- [Seller] --> [Property Details] --> [Contact Seller]
                              |
                              v
[Property Search] --> [Buyer] --> [Purchase Property] --> [Review Seller]
```

This can be visualized using tools like Microsoft Visio or Azure Architecture Center templates (e.g., "Web Application Architecture" adapted for real estate).

## Conceptual Model

The conceptual model provides a high-level view of the data entities and their relationships, independent of technology.

### Entities and Relationships:
- **User** (Buyer/Seller)
  - Attributes: UserID, Name, Email, Password, Role (Buyer/Seller)
- **Property**
  - Attributes: PropertyID, Title, Price, Location, Status (Available/Sold)
- **Review**
  - Attributes: ReviewID, Rating, Comment, Date
- **Transaction** (Optional, for purchase records)
  - Attributes: TransactionID, BuyerID, SellerID, PropertyID, Date

### Relationships:
- User **lists** Property (1 Seller : Many Properties)
- User **buys** Property (Many Buyers : Many Properties, via Transaction)
- User **reviews** User (Buyer reviews Seller: Many Reviews per Seller)
- Property **has** Review (Indirect via Seller)

### ER Diagram (Conceptual):

```
User (UserID, Name, Email, Password, Role)
  |
  | 1..* lists
  v
Property (PropertyID, Title, Price, Location, Status)
  ^
  | 1..* buys
  |
Buyer (subset of User)
  |
  | 1..* reviews
  v
Seller (subset of User) <-- Review (ReviewID, Rating, Comment, Date)
```

## Logical Model

The logical model refines the conceptual model with more detail, including data types and constraints, still technology-agnostic.

### Detailed Entities:

#### User
- UserID: Integer (Primary Key, Auto-Increment)
- Name: String (100 chars, Not Null)
- Email: String (100 chars, Unique, Not Null)
- Password: String (100 chars, Hashed, Not Null)
- Role: String (10 chars, e.g., 'Buyer' or 'Seller', Not Null)
- CreatedAt: DateTime (Default Now)

#### Property
- PropertyID: Integer (Primary Key, Auto-Increment)
- SellerID: Integer (Foreign Key to User.UserID, Not Null)
- Title: String (200 chars, Not Null)
- Price: Decimal (10,2, Not Null)
- Location: String (200 chars, Not Null)
- Status: String (20 chars, Default 'Available', e.g., 'Available'/'Sold')
- ListedAt: DateTime (Default Now)

#### Review
- ReviewID: Integer (Primary Key, Auto-Increment)
- BuyerID: Integer (Foreign Key to User.UserID, Not Null)
- SellerID: Integer (Foreign Key to User.UserID, Not Null)
- Rating: Integer (1-5, Not Null)
- Comment: Text (Optional)
- PostedAt: DateTime (Default Now)

#### Transaction (Optional for full tracking)
- TransactionID: Integer (Primary Key, Auto-Increment)
- BuyerID: Integer (Foreign Key to User.UserID, Not Null)
- SellerID: Integer (Foreign Key to User.UserID, Not Null)
- PropertyID: Integer (Foreign Key to Property.PropertyID, Not Null)
- Amount: Decimal (10,2, Not Null)
- TransactionDate: DateTime (Default Now)

### Relationships:
- User.UserID → Property.SellerID (One-to-Many)
- User.UserID → Review.BuyerID (One-to-Many)
- User.UserID → Review.SellerID (One-to-Many)
- Property.PropertyID → Transaction.PropertyID (One-to-One, if used)

This logical model can be implemented in SQL databases like Azure SQL Database.

## Next Steps
- **Class Diagram**: Based on this, create UML class diagram with attributes/methods.
- **Sequence Diagrams**: For specific user stories (e.g., "Write Review for Seller").
- **Architecture Diagram**: MVC pattern using Azure templates.

These models ensure the system supports buyer-seller interactions, property transactions, and reviews as per the project requirements.