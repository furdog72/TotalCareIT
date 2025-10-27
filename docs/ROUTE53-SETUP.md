# Route 53 Setup for totalcareit.ai

## Step 1: Create Hosted Zone in Route 53

1. Go to AWS Console → Route 53 → Hosted zones
2. Click **"Create hosted zone"**
3. Enter domain name: `totalcareit.ai`
4. Type: **Public hosted zone**
5. Click **"Create hosted zone"**

## Step 2: Note the Name Servers

After creating the hosted zone, Route 53 will assign 4 nameservers. They will look like:
- `ns-####.awsdns-##.com`
- `ns-####.awsdns-##.co.uk`
- `ns-####.awsdns-##.net`
- `ns-####.awsdns-##.org`

**IMPORTANT**: Copy these nameservers - you'll need them for Step 4.

## Step 3: Create DNS Records

### Option A: Manual Entry (Web Console)

Click **"Create record"** for each of the following:

#### Root Domain (A Records)
- **Record name**: (leave blank for root domain)
- **Type**: A
- **Value**:
  ```
  13.248.243.5
  76.223.105.230
  ```
- **TTL**: 3600

#### MX Record (Email)
- **Record name**: (leave blank)
- **Type**: MX
- **Value**: `0 totalcareit-ai.mail.protection.outlook.com`
- **TTL**: 3600

#### SPF Record (TXT)
- **Record name**: (leave blank)
- **Type**: TXT
- **Value**: `"v=spf1 include:spf.protection.outlook.com -all"`
- **TTL**: 3600

#### DMARC Record
- **Record name**: `_dmarc`
- **Type**: TXT
- **Value**: `"v=DMARC1; p=quarantine; rua=mailto:dmarc@totalcareit.ai"`
- **TTL**: 3600

#### Autodiscover (CNAME)
- **Record name**: `autodiscover`
- **Type**: CNAME
- **Value**: `autodiscover.outlook.com`
- **TTL**: 3600

#### DKIM Records (CNAME)
**Note**: You may need to get the exact selector names from Microsoft 365 admin portal.

- **Record name**: `selector1._domainkey`
- **Type**: CNAME
- **Value**: `selector1-totalcareit-ai._domainkey.totalcareit.onmicrosoft.com`
- **TTL**: 3600

- **Record name**: `selector2._domainkey`
- **Type**: CNAME
- **Value**: `selector2-totalcareit-ai._domainkey.totalcareit.onmicrosoft.com`
- **TTL**: 3600

#### Enterprise Registration/Enrollment (CNAME)
- **Record name**: `enterpriseregistration`
- **Type**: CNAME
- **Value**: `enterpriseregistration.windows.net`
- **TTL**: 3600

- **Record name**: `enterpriseenrollment`
- **Type**: CNAME
- **Value**: `enterpriseenrollment.manage.microsoft.com`
- **TTL**: 3600

#### Skype for Business / Teams (SRV Records)
- **Record name**: `_sipfederationtls._tcp`
- **Type**: SRV
- **Priority**: 100
- **Weight**: 1
- **Port**: 5061
- **Target**: `sipfed.online.lync.com`
- **TTL**: 3600

- **Record name**: `_sip._tls`
- **Type**: SRV
- **Priority**: 100
- **Weight**: 1
- **Port**: 443
- **Target**: `sipdir.online.lync.com`
- **TTL**: 3600

#### SIP/Lync CNAME Records
- **Record name**: `sip`
- **Type**: CNAME
- **Value**: `sipdir.online.lync.com`
- **TTL**: 3600

- **Record name**: `lyncdiscover`
- **Type**: CNAME
- **Value**: `webdir.online.lync.com`
- **TTL**: 3600

### Option B: AWS CLI Import (if you install AWS CLI)

```bash
# Create hosted zone (if not already created)
aws route53 create-hosted-zone --name totalcareit.ai --caller-reference $(date +%s)

# Get the hosted zone ID
ZONE_ID=$(aws route53 list-hosted-zones-by-name --dns-name totalcareit.ai --query "HostedZones[0].Id" --output text)

# Import records
aws route53 change-resource-record-sets --hosted-zone-id $ZONE_ID --change-batch file://route53-totalcareit-ai.json
```

## Step 4: Update GoDaddy Nameservers

1. Log into GoDaddy account
2. Go to **My Products** → **Domains**
3. Find `totalcareit.ai` and click **DNS** or **Manage DNS**
4. Look for **Nameservers** section
5. Click **Change** or **Manage**
6. Select **"I'll use my own nameservers"** or **"Custom"**
7. Enter the 4 AWS Route 53 nameservers from Step 2
8. Click **Save**

## Step 5: Verify DNS Propagation

After updating GoDaddy (wait 24-48 hours for full propagation):

```bash
# Check nameservers
dig totalcareit.ai NS +short

# Check MX records
dig totalcareit.ai MX +short

# Check SPF
dig totalcareit.ai TXT +short

# Check autodiscover
dig autodiscover.totalcareit.ai CNAME +short
```

## Step 6: Verify in Microsoft 365

1. Go to Microsoft 365 Admin Center
2. Navigate to **Settings** → **Domains**
3. Select `totalcareit.ai`
4. Click **"Verify DNS settings"** or **"Check DNS"**
5. Ensure all records show as configured correctly

## Important Notes

- **DNS Propagation**: Changes can take 24-48 hours to fully propagate
- **TTL**: Set to 3600 (1 hour) initially, can increase to 86400 (24 hours) after verification
- **DKIM Selectors**: The selector names (`selector1`, `selector2`) may differ - verify in M365 admin portal under **Settings** → **Domains** → **DNS records**
- **MX Record**: The format `totalcareit-ai.mail.protection.outlook.com` might vary - check your M365 admin portal for the exact value

## Troubleshooting

If email isn't working after DNS update:
1. Verify MX record in M365 admin portal matches Route 53
2. Check SPF record includes `include:spf.protection.outlook.com`
3. Verify DKIM CNAME records point to correct Microsoft selectors
4. Test email delivery with https://mxtoolbox.com/

## Current IP Addresses (from existing DNS)
- 13.248.243.5
- 76.223.105.230

These are preserved in the A records above.
