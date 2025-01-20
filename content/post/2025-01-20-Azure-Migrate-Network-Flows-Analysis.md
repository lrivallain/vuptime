---
title: "Tooling: Azure Migrate Network Flows Analysis"
date: "2025-01-20"
author: lrivallain
author_name: Ludovic Rivallain
categories:
- Azure
tags:
- Migrate
- Azure VMware Solution
- Tools
thumbnail: /images/thumbs/az-mdv-icon.png
toc: true
---

## Introduction

Migrating workloads to Azure, particularly Azure VMware Solution, is significantly streamlined by tools such as Azure Migrate and VMware HCX. However, some challenges remain. One major challenge is understanding network flows and preparing migration steps. Many users find it difficult to parse the data collected during Azure Migrate dependencies analysis and organize it into actionable migration waves.

### The problem

When conducting an Azure Migrate dependencies analysis, users often feel overwhelmed by the vast amount of network flow data and the challenge of understanding it. This data is essential for planning and executing a successful migration, but without the appropriate tools, it can be challenging to interpret and utilize effectively.

### The solution

To address this issue, I have developed a comprehensive solution: [Azure Migrate Network Flows Analysis](https://az-mdv.az.vupti.me/) ([Github repo](https://github.com/lrivallain/az-migrate-dep-visu)). This tool helps users understand network flow data by turning it into easy-to-read visuals. It helps users plan and execute migrations better, reducing errors and downtime. The tool also includes features like flows visualizations, filtered table and exports, making the migration process smoother and more likely to succeed.

## Features

- **CSV Import**: Import CSV files containing network flow data from Azure Migrate Dependency analysis
  - The data remains entirely within the browser and is never uploaded to a server, ensuring the protection of
    data privacy.
- **Data Processing**: Extract and process data from the uploaded CSV files.
- **Visualization**: Visualize the network flows using interactive graphs.
- **Filtering**: Filter the data based on various criteria such as IP addresses, ports, and VLANs.
- **CSV Download**: Download the filtered data as a CSV file.
- **VLANs**: Support for optional VLANs data columns in the CSV file and flow grouping.
  - Grouping items by VLAN or subnet is crucial for successful migration planning in an Azure VMware environment
    with HCX. Utilizing L2 extensions and preparing for extension cutover are essential steps to efficiently migrate
    workloads and prevent network issues.
- **Non RFC1918 IPs**: Regroup and filter non-RFC1918 IP addresses.

## How to use

1. **Upload CSV File**:
   - Navigate to the upload page.
   - Upload a CSV file containing network flow data.
   - The CSV file should have the following columns:
     - `Source server name`
     - `Source IP`
     - `Source application`
     - `Source process`
     - `Destination server name`
     - `Destination IP`
     - `Destination application`
     - `Destination process`
     - `Destination port`
     - `Source VLAN` (optional)
     - `Destination VLAN` (optional)

2. **View and Filter Data**:
   - After uploading, you will be redirected to the visualization page.
   - Use the filters to narrow down the data based on source IP, destination IP, port, and VLANs.
   - The data will be displayed in a table and as an interactive graph.

4. **Graph Interaction**:
   - Click on a connection to get some information about the flow statistics.

5. **Filter and group Non-RFC1918 IPs**:
   - Use the "Group Non-RFC1918" button to group non-RFC1918 IP addresses.
   - Table will be updated to simplify the search and filtering.
   - This enables to focus on Internet-bound traffic.

3. **Download Filtered Data**:
   - Click the "Download CSV" button to download the filtered data as a CSV file.

### Optional VLANs data

To help with the filtering, you can add optional VLANs data columns to the CSV file.

The columns should be named `Source VLAN` and `Destination VLAN`.

{{% notice info "Optional columns" %}}
These columns are not part of the original CSV file exported from Azure Migrate Dependency analysis.
{{% /notice %}}

The application will use this data to help filter and grouping resources in the visualization.

## Run your own instance

As the application is a JavaScript application, you can run it locally or host it on your own server. The application is available on [Github](https://github.com/lrivallain/az-migrate-dep-visu) and you can also use the [Docker image](https://hub.docker.com/r/lrivallain/az-migrate-dep-visu) to run it in a container.


## Test it !

The following integration provide a live test of the application with a test set of data. You can also access the application directly at [az-mdv.az.vupti.me](https://az-mdv.az.vupti.me/) and/or use your own data. Feedback is welcome!

<object data="https://az-mdv.az.vupti.me/#test" width="100%" height="1500px"
    title="Azure Migrate Network Flows Analysis"
    style="background: linear-gradient(white, white) padding-box,
                       linear-gradient(105deg, rgb(255 46 144) 0%, rgb(61 35 185) 100%) border-box;
               border: 4px solid transparent;
               border-radius: 10px;">
    Error: Embedded data could not be displayed, please visit the source: <a href="https://az-mdv.az.vupti.me/">Azure Migrate Network Flows Analysis</a>
</object>

## What's next ?

I plan to continue improving the tool by adding more features and enhancing the user experience. I welcome feedback and suggestions for future updates. If you have any questions or comments, please feel free to reach out to me.

I could also try to add some AI based features to help grouping workloads and suggest migrations waves based on the data. This could be a great addition to the tool.