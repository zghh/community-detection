# community-detection

## 参数设置
| Network | $n,m$ | $\sigma_s$ | $\lambda$ | $k$ | $tol$ | $k_{gt}$ | $k_{sc}$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| karate | $34,78$ | $1$ | $0.01$ | $3$ | $10^{-2}$ | $2$ | $7$ |
| football | $115,613$ | $10$ | $1$ | $12$ | $10^{-3}$ | $12$ | $12$ |
| polblogs | $1224,16715$ | $5$ | $1$ | $7$ | $10^{-2}$ | $2$ | $7$ |
| LRF | $1000,$ | $8$ | $1$ | $30$ | $10^{-4}$ |  | |

## 查询

查询包含特定节点的社区（如要求返回所有包含`id`为`1` 的节点的社区）

    match (n) where n.name = '001'
    with labels(n) as l
    match (n) where labels(n) = l
    return n

查询特定规模的社区（如要求返回所有节点数量⼤于`100`的社区）

    match (n) with n.name as name, labels(n)[0] as label
    with distinct label, count(*) as `count` 
    match (n) where labels(n)[0] = label and `count` > 100 return distinct n