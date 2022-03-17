# undefined 后端项目

## For Users

// TODO: 这里讲解后端配置文件的格式

## For Developers

请先阅读[项目规范](https://qynt1gy8vn.feishu.cn/docs/doccnLXFY9wOriyviGh5fv6NUgd)，然后再继续阅读本部分。

// TODO: 这里讲解怎么跑通 CI/CD

## 数据库模型

### UMS

#### User

+ id: BigAuto, primary_key
+ name: Text, indexed, 不允许重复
+ password: Text (sha256)
+ email: Text, indexed
+ avatar: Text (base64)
+ disabled: Boolean
+ createdAt: Float

#### SessionPool

+ sessionId: Text, indexed
+ user: FK
+ expiredAt: datetime (AUTO DELETE AFTER expiration)

#### Project

+ id: BigAuto, primary_key
+ title: Text, indexed
+ description: Text, indexed (Markdown)
+ disabled: Boolean
+ createdAt: Float

#### UserProjectAssociation

+ user: ForeignKey, indexed
+ project: ForeignKey, indexed
+ role: Text (enum "member", "dev", "qa", "sys", "supermaster")

// User + Project 联合唯一

#### ProjectInvitationAssociation

+ project: FK, ind
+ invitation: Text, ind（邀请码，用户注册使用直接加身份）
+ role: Text (enum role)

### RMS

#### Iteration

+ id: BigAuto, primary_key
+ project: ForeignKey, indexed
+ sid: Integer, 在项目中的 id
+ title: Text, 显示名
+ begin: Float
+ end: Float
+ disabled: Boolean
+ createdAt: Float

#### UserIterationAssociation

+ user: ForeignKey, indexed
+ iteration: ForeignKey, indexed

// user + iteration 联合唯一，代表 iteration 由用户主管

#### IR

+ id: BigAuto, pk
+ project: ForeignKey, indexed
+ title: Text, 显示名，要求与 project 联合唯一, indexed
+ description: Text (markdown)
+ rank: Integer // 同一个项目内，IR 按照 rank 顺序升序展示
+ createdBy: FK
+ createdAt: FK
+ disabled: Boolean

#### SR

+ id: BA, pk
+ project: FK, indexed
+ title: 同上, indexed
+ description: 同上
+ priority: Integer // 开发工作中这一件事的重要性，方便进行完成进度统计
+ rank: Integer // 同一个 IR 内，SR 按照 rank 顺序升序展示
+ state: enum("TODO", "WIP", "Reviewing", "Done")
+ createdBy: FK
+ createdAt: FK
+ disabled: Boolean

#### IRSRAssociation

出于一个 SR 可能解决多个 IR，一个 IR 可能对应多个 SR 的考虑，建立多对多联系。

+ IR: FK
+ SR: FK

#### SRIterationAssociation

+ SR: FK
+ iteration: FK

#### Service

+ id: BigAuto, pk
+ project: ForeignKey, indexed
+ title: Text, 显示名，要求与 project 联合唯一, indexed
+ description: Text (markdown)
+ rank: Integer // 同一个项目内，Service 按照 rank 顺序升序展示
+ createdBy: FK
+ createdAt: FK
+ disabled: Boolean

#### SR_Changelog

+ id: BigAuto, PK
+ project: FK
+ SR: FK
+ description: Text (Why It was changed?)
+ formerState:
+ changedBy: FK
+ changedAt: float

### RDTS

#### Repository

+ id: BigAuto, pk
+ url: string
+ project: ForeignKey
+ title: Text, 显示名，要求与 project 联合唯一, indexed
+ description: Text (markdown)
+ createdBy: FK
+ createdAt: FK
+ disabled: Boolean

#### Commit

+ id: BigAuto, pk
+ hash_id: string
+ repo: FK
+ title: Text
+ message: Text
+ createdBy: FK, allow_null
+ createdAt: float
+ disabled: Boolean

照着这个建：

+ https://gitlab.secoder.net/api/v4/projects/468/repository/commits

```json
{"id":"d6ba051d2b107287ee7a036e7defcadeb151e538","short_id":"d6ba051d","created_at":"2022-03-15T20:32:32.000+08:00","parent_ids":["4afe7fb64ef32997c5ee72465b09f4239bed8bea"],"title":"[SR.001.000] Fix routing issues: remove .htaccess, modify nginx settings","message":"[SR.001.000] Fix routing issues: remove .htaccess, modify nginx settings\n","author_name":"c7w","author_email":"admin@cc7w.cf","authored_date":"2022-03-15T20:32:32.000+08:00","committer_name":"c7w","committer_email":"admin@cc7w.cf","committed_date":"2022-03-15T20:32:32.000+08:00","web_url":"https://gitlab.secoder.net/undefined/frontend/-/commit/d6ba051d2b107287ee7a036e7defcadeb151e538"}
```

#### Merge Request

+ id: BigAuto, pk
+ merge_id: Integer
+ repo: FK
+ message: Text
+ state: enum
+ authoredBy: FK, allow_null
+ authoredAt: float, allow_null
+ reviewedBy: FK, allow_null
+ reviewedAt: float, allow_null
+ disabled: Boolean

照着这个建：

+ https://gitlab.secoder.net/api/v4/projects/468/merge_requests

```json
{"id":60,"iid":8,"project_id":468,"title":"[SR.001.002.F] Modify SonarQube properties","description":"[SR.001.002] Modify SonarQube properties","state":"merged","created_at":"2022-03-15T06:36:09.461Z","updated_at":"2022-03-15T06:45:56.029Z","merged_by":{"id":122,"name":"高焕昂","username":"2020010951","state":"active","avatar_url":"https://gitlab.secoder.net/uploads/-/system/user/avatar/122/avatar.png","web_url":"https://gitlab.secoder.net/2020010951"},"merged_at":"2022-03-15T06:45:26.204Z","closed_by":null,"closed_at":null,"target_branch":"dev","source_branch":"feature-001-002","user_notes_count":0,"upvotes":0,"downvotes":0,"author":{"id":122,"name":"高焕昂","username":"2020010951","state":"active","avatar_url":"https://gitlab.secoder.net/uploads/-/system/user/avatar/122/avatar.png","web_url":"https://gitlab.secoder.net/2020010951"},"assignees":[],"assignee":null,"source_project_id":468,"target_project_id":468,"labels":["infrastructure"],"work_in_progress":false,"milestone":null,"merge_when_pipeline_succeeds":false,"merge_status":"cannot_be_merged","sha":"0d4457764c1d034a8438f7e344de047d2f13b675","merge_commit_sha":"35c111aaa4f153f67aeb931d36d55c2a07ae0e85","squash_commit_sha":null,"discussion_locked":null,"should_remove_source_branch":null,"force_remove_source_branch":true,"reference":"!8","references":{"short":"!8","relative":"!8","full":"undefined/frontend!8"},"web_url":"https://gitlab.secoder.net/undefined/frontend/-/merge_requests/8","time_stats":{"time_estimate":0,"total_time_spent":0,"human_time_estimate":null,"human_total_time_spent":null},"squash":false,"task_completion_status":{"count":0,"completed_count":0},"has_conflicts":true,"blocking_discussions_resolved":true}
```



#### Issue

// 这里的 issue 不指议题，单指缺陷

+ id: BigAuto, pk
+ issue_id: Integer
+ repo: FK
+ message: Text
+ state: enum
+ authoredBy: FK, allow_null
+ authoredAt: float, allow_null
+ reviewedBy: FK, allow_null
+ reviewedAt: float, allow_null
+ disabled: Boolean

朝着这个建：

+ https://gitlab.secoder.net/api/v4/projects/468/issues

```json
{"id":167,"iid":8,"project_id":468,"title":"[SR.002.001] 增加前端部署用分支配置文件","description":"[SR.002.001] 增加前端部署用分支配置文件\n并完成 readme.md 中的有关说明","state":"opened","created_at":"2022-03-15T06:04:34.022Z","updated_at":"2022-03-15T06:04:34.022Z","closed_at":null,"closed_by":null,"labels":["infrastructure"],"milestone":null,"assignees":[{"id":122,"name":"高焕昂","username":"2020010951","state":"active","avatar_url":"https://gitlab.secoder.net/uploads/-/system/user/avatar/122/avatar.png","web_url":"https://gitlab.secoder.net/2020010951"}],"author":{"id":122,"name":"高焕昂","username":"2020010951","state":"active","avatar_url":"https://gitlab.secoder.net/uploads/-/system/user/avatar/122/avatar.png","web_url":"https://gitlab.secoder.net/2020010951"},"assignee":{"id":122,"name":"高焕昂","username":"2020010951","state":"active","avatar_url":"https://gitlab.secoder.net/uploads/-/system/user/avatar/122/avatar.png","web_url":"https://gitlab.secoder.net/2020010951"},"user_notes_count":0,"merge_requests_count":0,"upvotes":0,"downvotes":0,"due_date":"2022-03-22","confidential":false,"discussion_locked":null,"web_url":"https://gitlab.secoder.net/undefined/frontend/-/issues/8","time_stats":{"time_estimate":0,"total_time_spent":0,"human_time_estimate":null,"human_total_time_spent":null},"task_completion_status":{"count":0,"completed_count":0},"has_tasks":false,"_links":{"self":"https://gitlab.secoder.net/api/v4/projects/468/issues/8","notes":"https://gitlab.secoder.net/api/v4/projects/468/issues/8/notes","award_emoji":"https://gitlab.secoder.net/api/v4/projects/468/issues/8/award_emoji","project":"https://gitlab.secoder.net/api/v4/projects/468"},"references":{"short":"#8","relative":"#8","full":"undefined/frontend#8"},"moved_to_id":null}
```

#### CommitSRAssociation

+ commit: FK
+ SR: FK

#### MRSRAssociation

+ commit: FK
+ SR: FK

#### IssueSRAssociation

+ issue: FK
+ SR: FK

## 仓库访问令牌与 GitLab API

Repo > 设置 > 访问令牌

+ frontend: SxG2cW1sHs2vtZLdQxv4

## API

> **API 的外部呈现**
>
> 使用 类 Swagger 风格的生成器
>
> + https://github.com/axnsan12/drf-yasg/

若不加说明，[GET/POST] 方法的 [请求参数/请求体] 中均带有 sessionId 字段用于鉴权。

请**不要**在鉴权的时候大量复制粘贴相同的代码片段，应该使用一个专门的函数来鉴权。传入 sessionId 与所需权限，返回一个布尔值。

### `/ums/`

**所有请求都需要在cookie中包含sessionId，否则一律403 Forbidden** 

#### `[GET] /ums/user/`

Request params:

+ sessionId: str

Response:

+ code: 0 if success, 1 if not logged in
+ data
  + user: model_to_dict(User)
  + projects: filter and model_to_dict(Project)
  + schedule
    + done: {}
    + wip: {}
    + todo: {}

#### `[POST] /ums/login/`

Request Body:

- sessionId: str
- identity: str (username or email)
- password: str (already after md5, sha256 it and check)

Response:

+ code: 0 if success, 1 if already logged in, 2 if invalid identity, 3 if invalid password

#### `[POST] /ums/logout/`

Request Body:

+ sessionId: str

Response:

+ code: 0 if success, 1 if not logged in

#### `[POST] /ums/register/`

Request Body:

+ sessionId: str
+ name: str 
+ password: str (already after md5, sha256 it and check)
+ email: str (Remember to check if contains '@')
+ invitation: [Optional] str

Response:

+ code: 0 if success, 2 invalid invitation, 1 otherwise

#### `[GET] /ums/check_username_available/`

+ name: str

Response:

+ code: 0 if available, 1 otherwise

Explanation:

+ 这里 available 是说没有被占用，用户可以使用这个来注册

#### `[GET] /ums/check_email_available/`

+ email: str

Response:

+ code: 0 if available, 1 otherwise

#### `[POST] /ums/modify_user_role/`

+ project: int, project_id
+ user: int, user_id, user to be modified
+ role: str, the name of the new role, using (member, dev, qa, sys, supermaster)

Response:

+ code 0 if successful, 1 otherwise

#### `[POST] /ums/project/`

+ project: id of the project

Response:

+ code: 0 if successful, 1 otherwise
+ data: 
    + project: proj_to_list
    + users: filter and user_to_list

#### `[POST] /ums/modify_project/`

+ 

#### `[POST] /ums/refresh_invitation/`

#### `[GET] /ums/get_invitation/`


### `/rms/`

以下请求请自行设计并补全本文档的本部分，需要实现以下功能。

+ 获取用户参与的所有项目
+ 用户输入邀请码加入项目，成为开发工程师
+ 用户新建项目，成为系统工程师
+ 这里留一个**统一的接口**，比如 `[GET|POST] /rms/project/`
  + 给定某个项目ID，[READ/CREATE/UPDATE/DELETE, 以下简称 CRUD] IR（注意鉴权）
  + 给定某个项目ID，CRUD 所有的 SR
  + 给定某个项目ID，CRUD 所有的 Iteration
  + 给定某个项目ID，CRD IR-SR // A-B 代表两者之间的联系
  + 给定某个项目ID，CRD 的 SR-Iteration
  + 给定某个项目ID，CRUD Service
  + 给定某个项目ID，CRD User-Iteration

// 对于 CRUD，推荐的设计模式是：

+ READ 这个接口，直接返回所有数据
+ CREATE, UPDATE, DELETE 需要明确指定操作对象的类型，一次更新一条数据。合理的请求体例如：

```json
{"type": "sr", "project_id": 14, "operation": "update", "data": {"title": "更新后的 title"}, "sessionId": "balabala"}
{"type": "ir", "project_id": 14, "operation": "create", "sessionId": "balabala", "data": {
    // DATA HERE
}}
```

### `/rdts/`

以下请求请自行设计并补全本文档的本部分，需要实现以下功能。

这里留一个**统一的接口**，比如 `[GET|POST] /rdts/project/`

+ 给定某个项目ID
+ CRUD 所有的 Repo, Commit, MR
+ CRD 三种 Association

推荐的设计模式同上，方便前端计算渲染。



## Crontab

本项目需要定时任务拉取远端仓库的信息。

+ 在 Header 中添加 "PRIVATE-TOKEN: <your_access_token>" 
+ 访问 Repo 记录的对应 URL（如上 RDTS 部分记录的三个 URL）

我们需要以下定时任务：

+ 定时拉取最新的 Commit
+ 定时拉取最新的 PR
+ 定时拉取最新的 Issue

同时将数据库中的相应数据字段同步。



自动关联功能：

+ 定义相应的正则匹配表达式，当自动拉取的三种消息匹配到相应的正则表达式，便自动与 SR 的状态相关联。
