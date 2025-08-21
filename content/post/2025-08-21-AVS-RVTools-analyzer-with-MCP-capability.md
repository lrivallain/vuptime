---
title: "AVS RVTools Analyzer: Supercharging AVS migration assessments with AI capabilities"
date: "2025-08-21"
author: lrivallain
author_name: Ludovic Rivallain
categories:
- Azure
tags:
- vmware
- azure
- Migrate
- Azure VMware Solution
- RVTools
- MCP
- AI
thumbnail: /images/avs-rvtools-analyzer/thumb.svg
featureImage: /images/avs-rvtools-analyzer/mpc_analyze_summary_crop.png
toc: true
---

Migrating workloads from a VMware environment to an Azure VMware Solution (AVS) is a complex process that requires detailed planning and a careful understanding of the source infrastructure. To begin this process, tools like [RVTools](https://www.dell.com/en-us/shop/vmware/sl/rvtools) can be used to export a comprehensive snapshot of the VMware environment, providing a wealth of data about virtual machines, hardware configurations, resource usage, and more. This exported data becomes invaluable for assessing potential migration risks, identifying patterns, and flagging areas that may require attention or remediation ahead of the migration. By leveraging the insights from RVTools exports, we can better prepare for a smooth and efficient transition to the Azure VMware Solution.

To streamline and enhance this critical assessment step, I developed the [**AVS RVTools Analyzer**](https://github.com/lrivallain/avs-rvtools-analyzer). This tool is designed to quickly extract and highlight the most common patterns requiring attention from an RVTools export. By prioritizing “*migration-blocking*” risks over lower-priority warnings or informational items, the tool enables a sharper focus on issues that could derail a migration if left unaddressed. With the AVS RVTools Analyzer, it is easier to get a clear picture of all potential risks and challenges upfront, ensuring that teams can mitigate issues early and make informed decisions before committing further resources to the migration project.

## AVS RVTools Analyzer architecture

The AVS RVTools Analyzer is built as a unified FastAPI application that combines both:

* A web interface: `/`
* REST API: `/api`
* Model Context Protocol (MCP) server capabilities: `/mcp`

This architecture allows multiple kind of usage including:

* Starting the tool and uploading RVTools export files through the web interface
* Accessing analysis results via the REST API for automated processes
* Integrating with other AI tools using the MCP server capabilities and benefiting from advanced context-aware analysis and AI capabilities to suggest remediation actions


```goat
        +----------------------------+
        |            Users           |
        |----------------------------|
        |   Upload RVTools Export    |
        +----------------------------+
                      |
                      V
+---------------------------------------------+
|         AVS RVTools Analyzer (FastAPI)      |
|---------------------------------------------|
|                                             |
|  +-------------------+   +----------------+ |
|  |   Web Interface   |   |    REST API    | |
|  |-------------------|   |----------------| |
|  | (User File Upload |   | (Automated     | |
|  | & Report Views)   |   | Processes)     | |
|  +-------------------+   +----------------+ |
|                                             |
|  +---------------------------------------+  |
|  |     Model Context Protocol (MCP)      |  |
|  |---------------------------------------|  |
|  | (AI Integration with Context-Aware    |  | <-------> AI Tools (e.g., AI Models for
|  | Analysis & Suggestions)               |  |           Remediation Suggestions)
|  +---------------------------------------+  |
+---------------------------------------------+
                      |
                      V
        +----------------------------+
        |      Analysis Results      |
        |----------------------------|
        |  - Detect Migration Risks  |
        |  - Identify Remediation    |
        |    Actions & Warnings      |
        +----------------------------+
```

## Features at a Glance

The **AVS RVTools Analyzer** currently identifies **14 types of migration risks** across **five key categories**, helping you mitigate issues before moving to Azure VMware Solution (AVS).

### Risk Categories

* **Infrastructure** (2 risks):
  * **Incompatible ESX Versions** (Info): Detects version-related issues.
  * **Non-Intel Hosts** (Warning): Identifies hosts requiring cold migration, as AVS supports only Intel CPUs.

* **Virtual Machines** (6 risks):
  * **Suspended VMs** (Warning): Requires powered-on or powered-off states.
  * **Oracle VMs** (Info): Flags licensing cost concerns.
  * **VMware Tools Not Running** (Warning): Impacts migration via HCX.
  * **Large Provisioned VMs** (Warning): >10TB storage can delay migration.
  * **High vCPU VMs** (Blocking): Exceeds AVS core limits and must be downsized.
  * **High Memory VMs** (Info): May challenge AVS SKU memory limits.

* **Storage** (3 risks):
  * **Risky Disks** (Blocking): Unsupported "Independent" or RDM disks.
  * **Snapshots** (Warning): Increase migration complexity.
  * **CD-ROM Issues** (Warning): Cause boot or migration errors.

* **Networking** (2 risks):
  * **Non-DVS Switches** (Blocking): Requires distributed vSwitches to work with HCX network extension.
  * **DVPort Issues** (Warning): Detects misconfigurations (e.g., VLAN 0, promiscuous mode).

* **Compatibility** (1 risk):
  * **vUSB Devices** (Blocking): Unsupported on AVS and must be disconnected.

### Risk Severity Levels

| Severity Level | Description                  | Count |
|----------------|------------------------------|-------|
| **Info**       | Awareness items, no action   | 3     |
| **Warning**    | Important, should be fixed   | 7     |
| **Blocking**   | Critical, must be resolved   | 5     |

## Usage

### Installation and server startup

The tools is built with Python, available on [PyPI](https://pypi.org/project/avs-rvtools-analyzer/) and can be used with [`uv`](https://docs.astral.sh/uv/) or [`pip`](https://pip.pypa.io/en/stable/).

I will demonstrate the installation and usage of the tool using uv but you can use other installation methods if you prefer.

#### Prerequisites

Make sure you have [`uv`](https://docs.astral.sh/uv/) installed:

```bash
# On Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Quick Start with `uv`

Run the unified application with both web UI and MCP API:

```bash
# Run directly from PyPI (latest published version)
uv tool run avs-rvtools-analyzer

# Or run from source (current installed version)
uv run avs-rvtools-analyzer
```

With the default configuration, the application provides:

* Web interface: `http://127.0.0.1:8000` (upload and analyze files)
* API documentation: `http://127.0.0.1:8000/docs` (interactive OpenAPI docs)
* MCP tools: Available at `/mcp` endpoint for AI integration

### Web UI

The web interface allows users to upload files for analysis and view the results in a user-friendly format. It is also possible to print the analysis report as a PDF file or to export a CSV files of each section content.

![Upload form](/images/avs-rvtools-analyzer/upload_form.png)
![Analysis report in web UI](/images/avs-rvtools-analyzer/analyze_webui.png)

### REST API

REST API is fully documented using OpenAPI and can be used to automate the analysis process or integrate with other systems. `openapi.json` file is provided at the root of the project and integrated with Swagger UI and ReDoc:

![Swagger UI::picture-border](/images/avs-rvtools-analyzer/rest_api_swagger.png)

## AI Integration

{{% notice warning "Disclaimer" %}}
The AI integration in RVTools Analyzer may produce unexpected behavior or inaccuracies in the analysis results. It is strongly recommended to review the output carefully and validate it against known data. Additionally, please ensure that data privacy and compliance requirements are taken into account when using AI tools, as submitted data will be shared with AI systems.

The provided tools **run locally** to generate an analysis report from the uploaded RVTools file. When integrated with AI models, the data is processed and analyzed to deliver deeper insights and recommendations. If your AI models are not running in a local or secure environment, it is essential to verify that data is handled appropriately and in compliance with applicable regulations and your organization’s policies.
{{% /notice %}}

The AVS RVTools Analyzer now integrates with AI systems to deliver enhanced capabilities, such as advanced data analysis, predictive modeling, and automated decision-making.

To enable seamless interaction with AI models and tools, I implemented the [Model Context Protocol (MCP)](https://docs.astral.sh/mcp/), a standardized framework designed for AI integration. The MCP server is available at the `/mcp` endpoint and provides the following key tools:

1. **`analyze_file`**: Analyze RVTools file by providing a file path on the server.
2. **`analyze_uploaded_file`**: Upload and analyze RVTools Excel file.
3. **`list_available_risks`**: List all migration risks that can be assessed by this tool.
4. **`get_sku_capabilities`**: Get Azure VMware Solution (AVS) SKU hardware capabilities and specifications.

### Example of AI tool usage in Visual Studio Code

To demonstrate the usage of the AVS RVTools Analyzer with AI integration, I will provide an example of how to use the MCP tools within Visual Studio Code.

#### Create the MCP server in Visual Studio Code

1. Open the command palette (Ctrl+Shift+P) and run the `MCP: Add server` command.
2. This will prompt you for server type to add: `http` in our case.
3. Enter the server URL: `http://127.0.0.1:8000/mcp`.
4. Enter a name that fit your needs to recognize the server in available tooling.
4. In Copilot tools list, you can now check that MCP server capabilities are listed.
![MCP server capabilities in Visual Studio Code](/images/avs-rvtools-analyzer/mpc_in_visual_studio_code.png)

#### Using the MCP capacities to assess a RVTools file

1. In the Copilot prompt, enter a prompt like:

> I need a summarized analyze of AVS migration risks for the following file: `/\<path to your file\>/RVTools_export_all_test.xlsx`

2. When prompted for a confirmation before running a request to a MCP tool, review the details and confirm the action.
![Confirm MCP tool request](/images/avs-rvtools-analyzer/mpc_confirm_mcp_tool_use.png)

4. This should return a summarized analysis of the migration risks found in the provided RVTools file.
![MCP analyze summary](/images/avs-rvtools-analyzer/mpc_analyze_summary.png)

It is possible to dig deeper in the analysis by using specific prompts. For example:

> I need to analyze the migration risks related to VM snapshots in this file. Provide me the list of VMs and snapshots.

With the help of the used LLM model, the risk analysis is performed on the MCP server, then provided to the model to generate a detailed response based on the analysis results:

![Example of a deeper analyze with details about the related items and the process to follow for mitigation](/images/avs-rvtools-analyzer/mpc_deep_analyze.png)

#### Using the MCP integration to get SKU capabilities

Example of prompt:

> I want to compare CPU capabilities of AVS SKU AV36P and AV64

The MCP tool will return the CPU capabilities of the requested AVS SKU, allowing you to compare them easily:

![AVS SKU CPU Comparison: AV36P vs AV64](/images/avs-rvtools-analyzer/avs_sku_comparison.png)

## Conclusion

The integration of the AVS RVTools Analyzer with AI systems through the Model Context Protocol (MCP) significantly enhances its capabilities. Users can leverage the MCP tools to perform in-depth analysis of RVTools data, assess migration risks, and obtain detailed information about possible mitigation actions.

In the future, I plan to extend the tool to provide advanced features and add new risks detection based on user feedback and real field usage.

The project is open source and contributions are welcome. If you have ideas for new features, improvements, or additional risks to detect, feel free to open an issue or submit a pull request on the [GitHub repository](https://github.com/lrivallain/avs-rvtools-analyzer).