-- Create the NSSF members table
CREATE TABLE IF NOT EXISTS nssf_members (
    id SERIAL PRIMARY KEY,
    nssf_number VARCHAR(50) UNIQUE NOT NULL,
    member_name VARCHAR(255) NOT NULL,
    employer_name VARCHAR(255),
    empl_prim_number VARCHAR(100),
    dob DATE,
    age INTEGER,
    nin VARCHAR(100),
    father_name VARCHAR(255),
    mother_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the contributions table
CREATE TABLE IF NOT EXISTS contributions (
    id SERIAL PRIMARY KEY,
    nssf_number VARCHAR(50) NOT NULL,
    transaction_date DATE NOT NULL,
    reference_period VARCHAR(50),
    contributions_amount DECIMAL(15, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nssf_number) REFERENCES nssf_members(nssf_number)
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_nssf_number ON nssf_members(nssf_number);
CREATE INDEX IF NOT EXISTS idx_member_name ON nssf_members(member_name);
CREATE INDEX IF NOT EXISTS idx_employer_name ON nssf_members(employer_name);
CREATE INDEX IF NOT EXISTS idx_nin ON nssf_members(nin);

CREATE INDEX IF NOT EXISTS idx_contributions_nssf_number ON contributions(nssf_number);
CREATE INDEX IF NOT EXISTS idx_transaction_date ON contributions(transaction_date);

-- Create a view for common queries
CREATE OR REPLACE VIEW member_contributions_view AS
SELECT 
    m.nssf_number,
    m.member_name,
    m.employer_name,
    m.empl_prim_number,
    m.dob,
    m.age,
    m.nin,
    m.father_name,
    m.mother_name,
    c.transaction_date,
    c.reference_period,
    c.contributions_amount
FROM 
    nssf_members m
JOIN 
    contributions c ON m.nssf_number = c.nssf_number;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update the updated_at column
CREATE TRIGGER update_nssf_members_updated_at
BEFORE UPDATE ON nssf_members
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contributions_updated_at
BEFORE UPDATE ON contributions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();