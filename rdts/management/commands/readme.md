# A Scheduled Crwaler

## Usage
`manage.py schedule`

## Feature
每隔一定时间，遍历RemoteRepo，对所有enable_crawling的RemoteRepo仓库进行更新，更新方案暂定为哈希后逐一比对元素（O(n)）

在 stdout 运行信息

## Models
过程中记录了很多的信息

模型设计以注释形式直接写在models.py中


## Known Bugs
^C 似乎无法杀死该进程？（Windows环境）