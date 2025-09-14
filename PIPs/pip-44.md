---
title: Decentralized AI Chatbot and DAO Governance for Pactus
description: Integrates a decentralized AI chatbot for wallet operations and DAO governance, halves validator rewards to incentivize compute contributors, and enables WASM smart contract deployment.
author: Curtis Caudill (@cjcaudill79)
status: Draft
category: Core
created: 2025-09-13

---

## Abstract
Pactus's focus on accessibility, security, and sustainability via SSPoS makes it ripe for innovation. This proposal introduces a decentralized AI chatbot to simplify wallet operations and DAO governance, empowering users with natural language commands. By halving validator rewards to fund compute contributors, it fosters a sustainable ecosystem. A long-term goal allows developers to deploy WASM-based smart contracts via the chatbot, boosting dApp growth and positioning Pactus as a leader in AI-blockchain integration.

## Motivation
- Community Empowerment: A DAO aligns with Pactus's decentralized ethos, giving users a voice.
- AI Leadership: Positions Pactus as a pioneer, attracting tech-savvy participants.
- Adoption Growth: Simplifies interactions, potentially increasing users 2-5x.
- Sustainability: Reward adjustments support long-term economic stability.

## Specification
- **Architecture**: Features a frontend AI chatbot (web/mobile with NLP, sharded LLMs like Llama), a decentralized compute layer (node runners contribute GPU/CPU, tracked on-chain), and blockchain integration (Pactus APIs, PVM).
- **Reward Mechanism Modification**: Reduces validator rewards from 0.7 PAC/block (post-PIP-43) to 0.35 PAC/block, allocating 0.35 PAC/block to compute contributors, with the Foundation's 0.3 PAC/block unchanged. Rewards are distributed pro-rata based on FLOPs/hashrate, requiring minimal staking to prevent sybils, implemented via PIP and tested on testnet.
- **Wallet Functionality**: AI enables address creation, send/receive PAC, staking, and balance queries using the consumptional fee model.
- **DAO Governance**: Requires 100 PAC to propose, 10 PAC to vote, with a 1% voting cap (~420,000 PAC) per voter and 10% staked supply quorum. The Pactus team holds veto power due to execution responsibility, ensuring security. DAO proposals can be made and displayed for voting through the chatbot.
- **User Rewards**: Offers 0.001-0.01 PAC per interaction from fees/community pool, capped daily.

## Backwards Compatibility
Unsure

## Test Cases
- Test reward halving on testnet to ensure fair distribution.
- Simulate AI-driven wallet operations and DAO voting.

## Reference Implementation
- **AI Chatbot Development**: Uses PyTorch/TensorFlow for federated learning, fine-tuning Llama on wallet ops, governance, and WASM syntax. Nodes run WASM-based inference, tracked via on-chain proofs (e.g., Merkle proofs of FLOPs). Integrates Pactus JS SDK and gRPC for tx submission.

## Security Considerations
- Risks include reward resistance and low adoption.
- Mitigations: Gradual phasing and marketing via Pactus channels to encourage participation.

Added for additional context - Can delete if needed (Some redundancy)

1 Executive Summary
As you know, Pactus’s focus on accessibility, security, and sustainability via SSPoS positions
it for innovative advancements. This proposal introduces a decentralized AI chatbot
and DAO governance to enhance user accessibility, streamline wallet operations, and empower
community-driven decision-making. By halving validator rewards to incentivize compute contributors,
we foster a sustainable ecosystem aligned with Pactus’s vision. The long-term goal
enables developers to deploy WASM-based smart contracts via the chatbot, accelerating dApp
growth. This PIP aims to drive adoption, boost PAC utility, and establish Pactus as a leader in
AI-blockchain integration.

2 Proposed Integration: Decentralized AI Chatbot and DAO
2.1 High-Level Concept
The initiative introduces a decentralized AI chatbot as a user-friendly interface for wallet operations
and DAO governance via natural language (e.g., “Send 5 PAC” or “Vote on proposal
X”). Compute is provided by node runners, incentivized through restructured rewards. The
DAO enables PAC holders to propose and vote on upgrades, with team veto and voting caps for
fairness.

2.1.1 Why Beneficial
• Community Empowerment: DAO aligns with Pactus’s decentralized ethos.
• AI Leadership: Positions Pactus as a pioneer, attracting tech-savvy users.
• Adoption Growth: Simplifies interactions, potentially increasing users 2–5x.
• Sustainability: Reward changes support long-term economic stability.

2.2 Architecture
• Frontend AI Chatbot: Web/mobile app with NLP, built on sharded LLMs (e.g., Llama).
• Decentralized Compute Layer: Node runners contribute GPU/CPU; contributions tracked
on-chain.
• Blockchain Integration: Uses Pactus APIs and PVM for rewards and governance.
• Components:
– Wallet Module: Address generation, transactions, staking.
– Governance Module: Proposal creation, voting interface.

2.2.1 Why Advantageous
• Scalability: Distributed compute scales with network growth.
• Security: On-chain proofs and local key management reduce risks.
• Synergy: Integrates with decentralized storage and PVM.

Pactus AI & DAO Proposal
2.3 Reward Mechanism Modification
Adjust validator rewards (0.7 PAC/block post-PIP-43) to 0.35 PAC/block for validators and
0.35 PAC/block for compute contributors, maintaining the Foundation’s 0.3 PAC/block.
• Distribution: Compute rewards allocated pro-rata based on FLOPs/hashrate, with minimal
staking to prevent sybils.
• Implementation: Propose via PIP; test on testnet.

2.3.1 Why This is Good
• Inclusivity: Attracts AI contributors, expanding participation.
• Economic Balance: Extends emissions, supporting PIP-43 goals.
• Token Utility: Ties PAC value to AI usage, boosting demand.

2.4 Wallet Functionality
AI enables wallet operations: address creation, send/receive PAC, staking, and balance queries,
leveraging the consumptional fee model.

2.4.1 Benefits
• User-Friendly: Reduces onboarding friction, boosting retention.
• Ecosystem Growth: Complements GUI and web wallet enhancements.

2.5 DAO Governance
• Mechanics: Stake 100 PAC to propose, 10 PAC to vote; voting capped at 1% of total
supply ( 420,000 PAC) per voter; 10% staked supply quorum. Although the community
introduces proposals, the Pactus team retains veto power, as they would be responsible
for carrying them out, ensuring security and protocol integrity.
• AI Role: Guides staking/voting processes.
• Topics: Upgrades, reward changes, AI updates.

2.5.1 Why Beneficial
• Fairness: Voting caps prevent whale dominance.
• Alignment: Supports on-chain governance plans.
• Engagement: AI simplifies participation, increasing turnout.

2.6 User Rewards
Micro-rewards (0.001–0.01 PAC per interaction) from fees/community pool, capped daily.

Pactus AI & DAO Proposal
2.6.1 Advantages
• Adoption Incentive: Increases transaction volume.
• Token Stability: Promotes holding/staking, supporting PAC value.
3 Long-Term Goal: Smart Contract Deployment via AI Chatbot

3.1 High-Level Overview
Extend the AI chatbot to allow developers to deploy WASM-based smart contracts via natural
language, integrating with PVM to accelerate dApp development.

3.1.1 Why Beneficial
• Reduces development barriers.
• Drives ecosystem growth via dApps.
• Merges AI usability with blockchain programmability.

3.2 Technical Explanation
PVM supports WASM-based smart contracts.
1. Prerequisites:
• PVM operational.
• Pactus SDK (JS/Python) for tx building.
• AI fine-tuned for code parsing (e.g., via CodeBERT).

2. User Input Processing:
• Developer inputs: “Deploy contract: wasm code” or similar.
• AI parses code, language, and parameters using NLP.

3. Code Validation:
• Syntax check with linters (e.g., wasm-lint for WASM).
• Static analysis for vulnerabilities (e.g., custom WASM tools).
• Simulate execution in sandbox (wasmtime for WASM).

4. Compilation:
• Compile to PVM bytecode (e.g., wasm-pack or Pactus-specific compiler).
• AI handles errors, suggests fixes (e.g., missing imports).

5. Transaction Construction:
Pactus AI & DAO Proposal
• Build deployment tx via Pactus gRPC/REST API.
• Include bytecode, ABI, constructor args; calculate fees per PIP-31.

6. Signing and Broadcast:
• User approves/signs via chatbot (local key management).
• Broadcast tx to Pactus nodes.

7. Post-Deployment:
• Poll tx status via API; return contract address, logs.
• AI enables interaction (e.g., “Call function X with args Y”).

8. Decentralized Aspects:
• Offload compilation/validation to compute contributors (e.g., via distributed WebAssembly
runtimes).
• DAO governs supported languages and tools.

9. Security:
• Rate limits and stake requirements (e.g., 100 PAC) for deployments.
• AI flags risky code (e.g., reentrancy risks) for manual review or veto.
4 Technical Implementation Details
• AI Chatbot Development:
– Framework: Use PyTorch/TensorFlow for federated learning, sharding LLM across
nodes.
– Training: Fine-tune Llama or similar on blockchain-specific tasks (wallet ops, governance,
WASM syntax).
– Compute Contribution: Nodes run lightweight WASM-based inference tasks;
contributions tracked via on-chain proofs (e.g., Merkle proofs of FLOPs).
– APIs: Integrate Pactus JS SDK for wallet/governance; gRPC for tx submission.

5 Conclusion
This PIP leverages Pactus’s strengths to integrate a decentralized AI chatbot and DAO, enhancing
accessibility and governance. By building on PIP-43 and planned on-chain governance, it
ensures sustainability and positions Pactus as an AI-blockchain leader. We urge the team to
review and advance this proposal for community discussion.
